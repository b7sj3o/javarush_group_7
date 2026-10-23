from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import engine
from routers import auth, books, orders, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Таблиці й стартові дані тепер створює Alembic: alembic upgrade head
    yield
    await engine.dispose()  # після зупинки сервера


app = FastAPI(lifespan=lifespan)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(orders.router)
