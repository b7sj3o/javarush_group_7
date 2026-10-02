# Проект: Сервер зображень 2.0

## ТЗ — частина 1 (Docker + Python backend)

### Маршрути
- `GET /` — головна сторінка (обробляє backend)
- `POST /upload` — завантаження зображення (обробляє backend)
- `GET /images/<назва_файлу>` — отримати зображення (обробляє Nginx)

### Вимоги до завантаження
- Підтримувані формати: `.jpg`, `.png`, `.gif`
- Максимальний розмір файлу: **5 МБ**
- Генерувати унікальне ім'я для кожного файлу
- Зберігати файл у папку `/images`
- Повертати посилання на завантажений файл

### Логування
- Файл: `app.log` у папці `/logs`
- Формат: `[Дата/час] Тип: повідомлення`
- Логувати: успішні завантаження та помилки

### Структура проекту
```
project/
├── app.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── nginx.conf
├── images/         # volume для зображень
├── logs/           # volume для логів
└── frontend/       # статичні файли (HTML/CSS/JS)
```

### Порти
- **Nginx**: зовнішній порт `8080` → внутрішній `80`
- **Backend**: внутрішній порт `8000` (не виставляється назовні)
- Nginx проксіює запити до backend за адресою `http://backend:8000`

### Docker
- Два volumes: `images` і `logs`
- Запуск: `docker compose up --build`

---

## ТЗ — частина 2 (PostgreSQL + нові функції)

### Нові маршрути
- `GET /images-list` — список завантажених зображень з пагінацією
- `POST /delete/<id>` — видалення зображення за ID

### Таблиця `images` в PostgreSQL
```sql
CREATE TABLE images (
    id SERIAL PRIMARY KEY,
    filename TEXT NOT NULL,
    original_name TEXT NOT NULL,
    size INTEGER NOT NULL,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_type TEXT NOT NULL
);
```

### Сторінка `/images-list`
- Відображає таблицю зі стовпцями: назва файлу (посилання), оригінальна назва, розмір (КБ), дата/час, тип файлу
- Сортування за датою (новіші — першими)
- Кнопка "Видалити" для кожного рядка
- **Пагінація: 10 записів на сторінку** (`/images-list?page=2`)
- Кнопки "Наступна сторінка" / "Попередня сторінка"
- SQL: `SELECT * FROM images ORDER BY upload_time DESC LIMIT 10 OFFSET <зміщення>`

### Видалення зображень
- Видаляти запис з PostgreSQL: `DELETE FROM images WHERE id = <id>`
- Видаляти фізичний файл з папки `/images`
- Після успішного видалення → редірект на `/images-list`

### Резервне копіювання
- Папка `/backups` для зберігання бекапів
- Команда: `docker exec -t postgres_container pg_dump -U postgres images_db > backups/backup_<дата_та_час>.sql`
- Формат імені: `backup_2025-01-24_153000.sql`
- Відновлення: `docker exec -i postgres_container psql -U postgres images_db < backup.sql`

### PostgreSQL в Docker Compose
- Сервіс: `postgres`
- Підключення з Python через `psycopg2` (host = назва сервісу)

---

## Прийняті рішення по розбіжностях між ТЗ і кодом

| # | ТЗ | Поточний код | Рішення |
|---|----|----|--------|
| 1 | Порт Nginx `8080` | `docker-compose.yml`: `8080:80` | ✅ залишаємо `8080` |
| 2 | Маршрут завантаження `POST /upload` | Frontend: `POST /api/upload/` | ✅ залишаємо `/api/upload/` |
| 3 | Видалення `POST /delete/<id>` | Frontend: `DELETE /api/upload/<filename>` | ✅ залишаємо за іменем файлу + HTTP DELETE |
| 4 | Список `GET /images-list` | Frontend: `GET /api/upload/` | ✅ залишаємо `/api/upload/` |
| 5 | Макс. розмір файлу 5 МБ | Frontend: 1 МБ | ✅ змінено на **5 МБ** |
| 6 | Пагінація: 10 фіксовано | Frontend: 8 за замовчуванням | ✅ змінено на **10 фіксовано** |

## API маршрути (фактичні)

| Маршрут | Метод | Опис |
|---------|-------|------|
| `/api/upload/` | GET | Список зображень з пагінацією (`?page=1&limit=10&order=desc`) |
| `/api/upload/` | POST | Завантаження зображення |
| `/api/upload/<filename>` | DELETE | Видалення зображення за іменем файлу |
| `/images/<filename>` | GET | Отримати файл (обробляє Nginx) |
