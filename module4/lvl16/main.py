from typing import Annotated
from contextlib import asynccontextmanager

import httpx
from redis.asyncio import Redis
from fastapi import Depends, FastAPI, HTTPException, Request

from config import settings
from clients import get_country, get_place_location, get_weather
from schemes import Country, PlaceIn, PlaceOut, WeatherIn, WeatherOut


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


@app.get("/get_place_location/{name}", response_model=PlaceOut)
async def place_location(name: str, client: HttpClientDep): 
    return await get_place_location(client, name) 


@app.get("/weather/{name}", response_model=WeatherOut)
async def weather(name: str, client: HttpClientDep, redis: RedisDep): 
    location_data = await get_place_location(client, name) 
    
    data = WeatherIn(
        name=name,
        longitude=location_data.longitude,
        latitude=location_data.latitude,
    )
    return await get_weather(client, redis, data) 



@app.get("/country/{code}", response_model=Country)
async def weather(code: str, client: HttpClientDep): 
    return await get_country(client, code) 
    
    
    
