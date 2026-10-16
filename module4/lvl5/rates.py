"""Курс валют з відкритого API НБУ: зовнішній сервіс, до якого тести не повинні ходити по-справжньому."""

from typing import Annotated

import httpx
from fastapi import APIRouter, Depends, HTTPException, status

router = APIRouter(prefix="/rates", tags=["rates"])

NBU_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"


async def fetch_rate(client: httpx.AsyncClient, code: str) -> float | None:
    """Повертає курс валюти до гривні або None, якщо НБУ такої валюти не знає."""
    response = await client.get(NBU_URL, params={"valcode": code, "json": ""})
    response.raise_for_status()
    data = response.json()
    return data[0]["rate"] if data else None


async def get_http_client():
    """Залежність: один httpx-клієнт на запит. У тестах її підміняємо через dependency_overrides."""
    async with httpx.AsyncClient(timeout=10) as client:
        yield client


HttpClient = Annotated[httpx.AsyncClient, Depends(get_http_client)]


@router.get("/{code}")
async def get_rate(code: str, client: HttpClient):
    code = code.upper()
    try:
        rate = await fetch_rate(client, code)
    except httpx.HTTPError:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="НБУ не відповідає") from None
    if rate is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Валюти {code} немає")
    return {"code": code, "rate": rate}
