from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import settings
from database import create_client
from routers import books, stats
from seed import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.mongo = create_client()
    await init_db(app.state.mongo[settings.mongo_db])  # правило перевірки, індекси, стартові дані
    yield
    await app.state.mongo.close()  # після зупинки сервера


app = FastAPI(lifespan=lifespan)

app.include_router(books.router)
app.include_router(stats.router)
