from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis

from database import engine
from config import settings
from routers import auth, books, orders, users


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        yield
        await app.state.redis.aclose()
        await engine.dispose() 
        

    app = FastAPI(lifespan=lifespan)


    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(books.router)
    app.include_router(orders.router)
    
    return app

app = create_app()




