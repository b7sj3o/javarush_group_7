"""Standalone backup script — produces a timestamped pg_dump file in backups/.

Run on the HOST machine (not inside Docker):
    python backend/backup.py

Requires the postgres container to be running.

Restore from a backup:
    docker exec -i image_server_db psql -U postgres images_db < backups/<file>.sql
"""

import logging
import os
import subprocess
import sys
from datetime import datetime


BACKUPS_DIR        = "backups"
POSTGRES_CONTAINER = os.getenv("POSTGRES_CONTAINER", "image_server_db")
DB_NAME            = os.getenv("DB_NAME",  "images_db")
DB_USER            = os.getenv("DB_USER",  "postgres")


def create_backup() -> str:
    """Run pg_dump inside the postgres container and save the SQL to a file.

    Steps:
      1. Ensure BACKUPS_DIR exists.
      2. Build timestamped filename: backup_YYYY-MM-DD_HHMMSS.sql
      3. docker exec -t <container> pg_dump -U <user> <db>
      4. Write stdout to the file.
      5. Log success and return the file path.
    """
    os.makedirs(BACKUPS_DIR, exist_ok=True)

    ts   = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    path = os.path.join(BACKUPS_DIR, f"backup_{ts}.sql")

    logging.info(f"Starting backup → {path}")

    result = subprocess.run(
        ["docker", "exec", "-t", POSTGRES_CONTAINER, "pg_dump", "-U", DB_USER, DB_NAME],
        capture_output=True,
    )

    if result.returncode != 0:
        err = result.stderr.decode(errors="replace")
        logging.error(f"pg_dump failed: {err}")
        raise RuntimeError(f"pg_dump exited {result.returncode}: {err}")

    with open(path, "wb") as f:
        f.write(result.stdout)

    logging.info(f"Backup complete: {path}")
    return path


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler()],
    )
    try:
        saved = create_backup()
        print(f"Saved: {saved}")
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
