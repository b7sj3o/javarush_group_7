# Сервер зображень 2.0

## Запуск

```powershell
docker compose up --build
```

Nginx: http://localhost:80

## Резервне копіювання БД

Папка `./backups` змонтована в контейнер postgres як `/backups`, тож pg_dump
пише дамп **усередині** контейнера (через `-f`, без редіректу) — чистий UTF-8.

### Створити бекап

```bash
./backups/backup.sh
```

Створить `backups/backup_<дата>.sql` (напр. `backup_2025-01-24_153000.sql`).

### Відновити з бекапу

```bash
./backups/restore.sh backup_2025-01-24_153000.sql
```

### Команди вручну (без скриптів)

```bash
# бекап
docker exec postgres pg_dump -U postgres -d image_hosting -f /backups/backup.sql
# відновлення
docker exec -i postgres psql -U postgres -d image_hosting -f /backups/backup.sql
```

### Автоматичні бекапи (раз на 2 години)

Сервіс `backup` у docker-compose — окремий контейнер на образі `postgres:17`,
який у циклі робить `pg_dump` і спить (див. `backups/auto-backup.sh`).
Працює автоматично, поки запущений `docker compose up`.

Інтервал змінюється через `INTERVAL` (секунди) у docker-compose:
`INTERVAL: 3600` = щогодини.

## Персистентність

- **Дані БД** живуть у named volume `postgres_data` — переживають `docker compose down`.
  Видаляються лише при `docker compose down -v`.
- **Бекапи** лежать на хості в `./backups` — не залежать від volume взагалі.
- **Зображення** і **логи** — bind-mount у `./images` та `./logs`.

Тому перед `docker compose down -v` варто зробити бекап — це єдиний спосіб
відновити дані після видалення volume.
