# ПОТУЖНО Shop — React-фронтенд

SPA-версія магазину поверх DRF API (`/api/v1/`). Повний розбір архітектури —
у [docs/lessons/L21.5_react.md](../docs/lessons/L21.5_react.md).

## Стек

- **Vite + React 19** (JavaScript, без TypeScript — свідомо, для простоти курсу)
- **React Router 7** — маршрутизація
- **Tailwind CSS 4** — стилі; дизайн-токени в `src/index.css`
- JWT-автентифікація (SimpleJWT) з автоматичним refresh при 401

## Запуск

```bash
# бекенд повинен працювати на 127.0.0.1:8000
npm install
npm run dev        # http://localhost:5173
```

Адреса API читається з `.env` → `VITE_API_URL`.

## Структура src/

| Папка | Що всередині |
|-------|--------------|
| `api/` | Шар роботи з API: `client.js` (fetch + JWT + refresh), по файлу на ресурс |
| `context/` | `AuthContext` (хто залогінений, ролі), `ToastContext` (сповіщення) |
| `hooks/` | Перевикористовувані хуки (`useDebounce`) |
| `components/` | UI-компоненти: `layout/`, `ui/`, `product/`, `reviews/` |
| `pages/` | Сторінки-маршрути; `pages/manage/` — тільки для менеджерів каталогу |
| `utils/` | Форматування (ціни, дати), розбір помилок DRF |

## Команди

```bash
npm run dev      # dev-сервер з HMR
npm run build    # production-збірка в dist/
npm run lint     # ESLint
```
