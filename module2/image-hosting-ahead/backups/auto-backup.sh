#!/bin/sh
# Автоматичний бекап у циклі — запускається в окремому контейнері (sidecar).
# Працює, поки запущений docker compose. Не потребує cron-демона.

# INTERVAL — пауза між бекапами в секундах. Береться зі змінної оточення,
# а якщо не задана — 7200 (2 години). ${VAR:-default} = значення або дефолт.
INTERVAL="${INTERVAL:-7200}"

# Чекаємо, поки PostgreSQL буде готовий приймати з'єднання.
# pg_isready повертає 0, коли БД піднялась; until крутиться, поки не 0.
until pg_isready -h postgres -U postgres -d image_hosting; do
  echo "Чекаю postgres..."
  sleep 2
done

# Безкінечний цикл: зробити бекап -> поспати INTERVAL -> повторити.
while true; do
  ts=$(date +%Y-%m-%d_%H%M%S)
  # pg_dump під'єднується до контейнера postgres по мережі (-h postgres).
  # Пароль береться зі змінної PGPASSWORD (задана в docker-compose).
  if pg_dump -h postgres -U postgres -d image_hosting -f "/backups/backup_${ts}.sql"; then
    echo "OK: backup_${ts}.sql"
  else
    echo "FAIL: pg_dump (код $?)"
  fi
  sleep "$INTERVAL"
done
