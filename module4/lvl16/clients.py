import httpx
from fastapi import HTTPException
from redis.asyncio import Redis

from config import settings
from schemes import Country, PlaceIn, PlaceOut, WeatherIn, WeatherOut


COUNTRY_QUERY = """
query GetCountry($code: ID!) {
  country(code: $code) { name capital currency emoji }
}
"""


async def call(client: httpx.AsyncClient, method: str, url: str, **kwargs) -> httpx.Response:
    try:
        response = await client.request(method, url, **kwargs)
        response.raise_for_status()
        return response
    except httpx.TimeoutException:
        raise HTTPException(504, f"{url} не відповів вчасно") from None
    except httpx.ConnectError:
        raise HTTPException(503, f"Не вдалося підключитися до {url}") from None
    except httpx.HTTPStatusError as e:
        raise HTTPException(502, f"{url} повернув {e.response.status_code}") from None
    
    
async def get_country(client: httpx.AsyncClient, code: str) -> Country:
    response = await call(
        client, "POST", settings.countries_url, json={"query": COUNTRY_QUERY, "variables": {"code": code.upper()}}
    )
    data = response.json()["data"]["country"]
    if data is None:
        raise HTTPException(404, f"Країни {code} не існує")
    return Country.model_validate(data)


async def get_place_location(client: httpx.AsyncClient, name: str) -> PlaceOut:
    response = await call(
        client,
        "GET",
        settings.geocoding_url,
        params={
            "name": name,
            "count": 1
        }
    )
    
    return PlaceOut.model_validate(response.json().get("results")[0])
    

async def get_weather(client: httpx.AsyncClient, redis: Redis, data: WeatherIn) -> WeatherOut:
    key = f"weather:{data.name}"
    if cached := await redis.get(key):
        return WeatherOut.model_validate_json(cached)
    
    print('============')
    print(data.model_dump())
    print('============')
    
    response = await call(
        client,
        "GET",
        settings.weather_url,
        params={
            "latitude": data.latitude,
            "longitude": data.longitude,
            "current": "temperature_2m,wind_speed_10m"
        }
    )
    
    weather = WeatherOut.model_validate(response.json()["current"])
    await redis.setex(key, settings.cache_ttl, weather.model_dump_json())
    return weather