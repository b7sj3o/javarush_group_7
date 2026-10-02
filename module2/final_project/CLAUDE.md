# Image Server 2.0 — Architecture Guide

Educational project. A small web service that accepts image uploads, stores
metadata in PostgreSQL, and serves the files back through Nginx.

---

## Layout

```
final_project/
├── CLAUDE.md            this file
├── requirements.txt     Python deps: Pillow, psycopg2-binary
├── Dockerfile           multi-stage build of the backend image
├── compose.yaml         app + nginx + db
├── nginx.conf           /images/ + /static/ from disk, rest → backend
│
├── backend/             ALL Python code
│   ├── main.py          entry point: logging, schema init, router
│   ├── handlers.py      one function per route (home, upload, list, delete)
│   ├── db.py            psycopg2 connection + CRUD on `images`
│   ├── validators.py    extension / size / Pillow image-integrity checks
│   ├── templates.py     loads HTML files, fills placeholders
│   ├── config.py        env vars, paths, limits, pagination size
│   └── backup.py        standalone pg_dump runner
│
├── frontend/            client-facing assets
│   ├── templates/       base.html · home.html · list.html · error.html
│   └── static/          style.css
│
├── db/                  database artifacts (SQL, not Python)
│   └── init.sql         schema for `images`; auto-run on first DB start
│
└── (runtime, not committed)
    ├── images/          uploaded files     → mounted into app + nginx
    ├── logs/            app.log            → mounted into app
    └── backups/         pg_dump .sql files → produced by backend/backup.py
```

### Why this split

- **backend / frontend / db** is a clear three-way separation that maps to the three
  things a reader cares about: server logic, what the user sees, what lives in Postgres.
- No `services/` + `repositories/` + `dto/` cathedral. Five routes and one table
  don't need it — `handlers.py` calls `db.py` directly.
- No migration tool (Alembic). One stable table is fine with `init.sql`.
- Infra files (`Dockerfile`, `compose.yaml`, `nginx.conf`) stay at the repo root —
  that's where `docker compose up` expects them; hiding them inside `infra/` would
  cost ergonomics for no real benefit at this size.

---

## Module Responsibilities

| Module                | Responsibility                                                |
|-----------------------|---------------------------------------------------------------|
| `backend/main.py`     | Boot: configure logging, init schema, register routes, serve. |
| `backend/handlers.py` | One function per route — HTTP plumbing only.                  |
| `backend/db.py`       | Connect, run queries, return plain dicts/ints.                |
| `backend/validators.py`| File-extension / size / image-bytes checks.                  |
| `backend/templates.py`| Load HTML from `frontend/templates`, substitute placeholders. |
| `backend/config.py`   | Env vars, paths, limits — no logic.                           |
| `backend/backup.py`   | Spawns `pg_dump` against the postgres container.              |

Rule of thumb: **handlers** orchestrate, **validators / db / templates** do one job each.

---

## Services (compose.yaml)

### `app`
Python backend. Listens on `8000`. Volumes: `images/`, `logs/`. Depends on `db`.

### `nginx`
Public entrypoint on host port `8080` → container `80`.
- `/images/<file>` → disk
- `/static/<file>` → disk
- everything else → `http://app:8000`

### `db`
PostgreSQL. `db/init.sql` is mounted into `/docker-entrypoint-initdb.d/` so the
schema is created automatically on first start. Data persisted in named volume `db_data`.

---

## Database Schema (`db/init.sql`)

```sql
CREATE TABLE images (
    id            SERIAL PRIMARY KEY,
    filename      TEXT      NOT NULL,   -- server-generated unique name
    original_name TEXT      NOT NULL,
    size          INTEGER   NOT NULL,
    upload_time   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type     TEXT      NOT NULL
);
```

---

## Routes

| Method | Path                  | Served by | What it does                         |
|--------|-----------------------|-----------|--------------------------------------|
| GET    | `/`                   | backend   | Upload form                          |
| POST   | `/upload`             | backend   | Validate, save file + DB row         |
| GET    | `/images-list`        | backend   | Paginated table (10 per page)        |
| POST   | `/delete/<id>`        | backend   | Delete row + file, redirect to list  |
| GET    | `/images/<filename>`  | nginx     | Raw image from `/images/` volume     |
| GET    | `/static/<filename>`  | nginx     | CSS / JS                             |

Pagination: `/images-list?page=N` — `LIMIT 10 OFFSET (N-1)*10`.

---

## Upload Flow

1. `handlers.upload` parses multipart body.
2. `validators` checks extension, size, Pillow-decodability.
3. `validators.generate_unique_name` produces a UUID-based filename.
4. Bytes written to `IMAGES_DIR`.
5. `db.insert_image` writes metadata; if it fails the file is removed.
6. Success page / redirect to `/images-list`.

Every step writes to `logs/app.log` in the format `[YYYY-MM-DD HH:MM:SS] Level: message`.

---

## Validation Rules

| Rule            | Value                            |
|-----------------|----------------------------------|
| Extensions      | `.jpg`, `.jpeg`, `.png`, `.gif`  |
| Max size        | 5 MB                             |
| Real-image check| Pillow `Image.open(...).verify()`|

Failures → HTTP 400 with `error.html`.

---

## Backup

```bash
python backend/backup.py
```

- Calls `docker exec` against the postgres container, runs `pg_dump`.
- Output: `backups/backup_YYYY-MM-DD_HHMMSS.sql`.

Restore:

```bash
docker exec -i image_server_db psql -U postgres images_db < backups/<file>.sql
```

---

## Run

```bash
docker compose up --build
```

| Where                            | What                          |
|----------------------------------|-------------------------------|
| http://localhost:8080            | Site (through Nginx)          |
| http://localhost:8080/images-list| Image list page               |
| http://localhost:8000            | Backend (bypassing Nginx)     |
