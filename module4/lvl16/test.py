import httpx
import asyncio

async def fetch_posts():
    async with httpx.AsyncClient() as client:
        # 'await' призупиняє виконання, поки ми чекаємо на відповідь від мережі
        response = await client.get("https://jsonplaceholder.typicode.com/posts/1")
        # Перевірити, чи був запит успішним (статус 2xx)
        response.raise_for_status()
        return response.json()
    
    
async def main():
    data = await fetch_posts()
    print(data)

asyncio.run(main())




# ===================================

from typing import Annotated
from contextlib import asynccontextmanager

import httpx
from redis.asyncio import Redis
from fastapi import Depends, FastAPI, HTTPException, Request

from config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.http_client = httpx.AsyncClient(timeout=settings.timeout)
    app.state.redis = Redis.from_url(settings.redis_url, decode_responses=True)
    
    yield
    
    await app.state.http_client.aclose()
    await app.state.redis.aclose()
    

app = FastAPI(lifespan=lifespan)


def get_http_client(request: Request) -> httpx.AsyncClient:
    return request.app.state.http_client


def get_redis(request: Request) -> httpx.AsyncClient:
    return request.app.state.redis


HttpClientDep = Annotated[httpx.AsyncClient, Depends(get_http_client)]
RedisDep = Annotated[Redis, Depends(get_redis)]


@app.get("/external-users/{user_id}")
async def get_external_user(user_id: int, client: HttpClientDep):
    url = f"https://jsonplaceholder.typicode.com/users/{user_id}"
    try:
        response = await client.get(url)
        response.raise_for_status()
    except httpx.HTTPStatusError as err:
        raise HTTPException(status_code=response.status_code, detail=err.response.text)
        
    return response.json()
    
    

@app.post("/create-external-post/")
async def create_external_post(title: str, body: str, client: HttpClientDep):
    url = "https://jsonplaceholder.typicode.com/posts"
    payload = {"title": title, "body": body, "userId": 1}
    response = await client.post(url, json=payload)
    return {"status_code": response.status_code, "response_data": response.json()}