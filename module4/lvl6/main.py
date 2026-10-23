from contextlib import asynccontextmanager

from fastapi import FastAPI

from seed import init_db
from routers import books, users, orders, auth
from database import engine


def create_app():
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await init_db(engine) # до першого запиту
        yield
        await engine.dispose() # після зупинки сервера

    app = FastAPI(lifespan=lifespan)
    
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(books.router)
    app.include_router(orders.router)
    
    return app

app = create_app()

