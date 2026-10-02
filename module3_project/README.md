# 🛍️ ПОТУЖНО Shop

Навчальний проєкт **Модуля 3 (Django)** курсу Python Fullstack у JavaRush.

Це **наскрізний проєкт**: протягом 25 лекцій ми крок за кроком будуємо один цілісний застосунок —
інтернет-магазин одягу та взуття з каталогом товарів, відгуками та особистим кабінетом.
На кожній парі перша половина — теорія з презентації, друга — застосування теми на ПОТУЖНО Shop.

Архітектура підсумкового проєкту: **Django — лише бекенд (REST API + GraphQL), React — фронтенд.**

---

## Що вміє застосунок

- Каталог товарів: категорії, бренди, розміри, ціна, опис; фільтри та пошук.
- Картка товару з відгуками та оцінками (1–5); середній рейтинг.
- Особистий список «Обране».
- Реєстрація / вхід (JWT), профіль користувача.
- Ролі: «Менеджер каталогу» та «Модератор відгуків»; адмінка Django для керування ними.
- REST API з пагінацією, фільтрами, throttling і документацією (Swagger).
- GraphQL-ендпоінт для гнучких вкладених запитів.
- Docker + nginx: увесь стек піднімається однією командою.

> Повний план занять — у [`docs/ROADMAP.md`](docs/ROADMAP.md).
> Архітектура й моделі — у [`docs/PROJECT.md`](docs/PROJECT.md).
> Покрокові конспекти пар — у [`docs/lessons/`](docs/lessons/).

---

## Стек

| Шар | Технологія |
|-----|------------|
| Мова | Python 3.12+ |
| Фреймворк | Django 6.0 |
| База даних | PostgreSQL 17 |
| API | Django REST Framework + SimpleJWT |
| GraphQL | graphene-django |
| Фронтенд | React 19 + Vite + React Router + Tailwind CSS (`frontend/`) |
| Прод | Docker Compose: PostgreSQL + gunicorn + nginx |
| Тести | pytest-django |

---

## Запуск через Docker (як у проді)

Потрібен лише Docker Desktop. Піднімає три контейнери: `db` (PostgreSQL), `backend` (Django + gunicorn),
`nginx` (React-збірка + reverse-proxy на Django).

```bash
copy .env.example .env          # Windows; на macOS/Linux: cp .env.example .env
# у .env обов'язково зміни DJANGO_SECRET_KEY

docker compose up --build -d    # зібрати образи й запустити
docker compose exec backend python manage.py seed_products    # демо-дані (опційно)
docker compose exec backend python manage.py createsuperuser  # адмін для /admin/
```

Відкрити: http://localhost/ — магазин · http://localhost/admin/ — адмінка ·
http://localhost/api/schema/swagger-ui/ — документація API · http://localhost/graphql/ — GraphiQL.

```bash
docker compose logs -f backend  # логи Django
docker compose down             # зупинити (дані в базі зберігаються у volume)
docker compose down -v          # зупинити й видалити базу
```

Як це працює: nginx слухає порт 80. Запити на `/api/`, `/admin/`, `/graphql/` він проксить
на gunicorn (`backend:8000`), `/static/` віддає зі спільного volume (туди `collectstatic` складає
статику адмінки), а все інше — це React-збірка з `index.html` для будь-якого маршруту.
`entrypoint.sh` при кожному старті `backend` застосовує міграції та збирає статику.

> HTTPS не входить у цю конфігурацію. На реальному сервері простіше за все поставити
> перед nginx Cloudflare або Caddy, а в `.env` додати домен у `DJANGO_ALLOWED_HOSTS`
> і `DJANGO_CSRF_TRUSTED_ORIGINS=https://твій-домен`.

---

## Локальна розробка (для студента)

Бекенд і фронтенд запускаються окремо; PostgreSQL — свій локальний або в Docker.

```bash
# 1. Клонувати репозиторій
git clone <url> module3_project
cd module3_project
copy .env.example .env          # і відредагувати під свою базу

# 2. Django
cd potuzhno_shop
python -m venv .venv
.venv\Scripts\activate          # macOS / Linux: source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_products  # демо-дані: товари, відгуки, користувачі demo1..3 / demo12345
python manage.py runserver      # http://127.0.0.1:8000/

# 3. React — в окремому терміналі
cd frontend
npm install
npm run dev                     # http://localhost:5173
```

Vite dev-сервер ходить на API за адресою з `frontend/.env` (`VITE_API_URL=http://127.0.0.1:8000/api/v1`).

Тести: `cd potuzhno_shop && pytest`.

---

## Структура репозиторію

```
module3_project/
├── docker-compose.yml      # db + backend + nginx
├── nginx/
│   ├── Dockerfile          # збірка React → образ nginx
│   └── default.conf        # reverse-proxy та роздача статики
├── frontend/               # React SPA (див. frontend/README.md)
└── potuzhno_shop/          # Django-проєкт
    ├── Dockerfile
    ├── entrypoint.sh       # migrate + collectstatic перед стартом gunicorn
    ├── manage.py
    ├── requirements.txt
    ├── potuzhno_shop/      # settings, urls, wsgi
    ├── tests/              # pytest
    └── apps/
        ├── catalog/        # товари, категорії, бренди, розміри: models + serializers + views + filters
        ├── reviews/        # відгуки
        ├── accounts/       # Profile, реєстрація, JWT, /users/me/
        ├── contact/        # форма зворотного зв'язку (без моделі)
        └── api/            # спільне: маршрути /api/v1/, permissions, pagination, GraphQL-схема
```

Кожен feature-app (`catalog`, `reviews`, `accounts`, `contact`) містить свої моделі,
серіалізатори та view. `api/urls.py` збирає їх під `/api/v1/`, а `api/schema.py` —
GraphQL поверх тих самих моделей.
