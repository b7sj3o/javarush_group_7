from contextlib import asynccontextmanager

from fastapi import FastAPI
from redis.asyncio import Redis
from pymongo import AsyncMongoClient

from database import engine
from config import settings
from routers import auth, books, orders, users, reviews, logs
from mongo_client import init_mongo


def create_app():
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
        app.state.mongo = AsyncMongoClient(settings.mongo_url, serverSelectionTimeoutMS=3000)
        await init_mongo(app.state.mongo[settings.mongo_db])
        yield
        await app.state.redis.aclose()
        await app.state.mongo.close()
        await engine.dispose() 
        

    app = FastAPI(lifespan=lifespan)


    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(books.router)
    app.include_router(orders.router)
    app.include_router(reviews.router)
    app.include_router(logs.router)
    
    return app

app = create_app()




