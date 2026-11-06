"""Гонка за останнім товаром: 20 покупців одночасно, на складі 5.

Сервер має бути запущений: uvicorn main:app
Запуск: python race_demo.py unsafe | locked | atomic
"""

import asyncio
import sys
from collections import Counter

import httpx

BASE = "http://127.0.0.1:8000"
PATHS = {"unsafe": "/orders/unsafe", "locked": "/orders", "atomic": "/orders/atomic"}
PRODUCT_ID = 51
BUYERS = 20


async def main(mode: str) -> None:
    async with httpx.AsyncClient(base_url=BASE, timeout=60) as client:
        await client.patch(f"/products/{PRODUCT_ID}", json={"stock": 5})
        requests = [
            client.post(PATHS[mode], json={"user_id": user_id, "product_id": PRODUCT_ID})
            for user_id in range(1, BUYERS + 1)
        ]
        responses = await asyncio.gather(*requests)  # усі 20 летять одночасно
    codes = Counter(r.status_code for r in responses)
    stock_left = [r.json()["stock_left"] for r in responses if r.status_code == 201]
    print(f"{mode}: на складі було 5, покупців {BUYERS}")
    print(f"  куплено (201): {codes[201]}, відмов (409): {codes[409]}, інше: {codes.total() - codes[201] - codes[409]}")
    print(f"  оформлено понад залишок: {max(codes[201] - 5, 0)}")
    print(f"  залишки у відповідях: {sorted(stock_left, reverse=True)}")


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "unsafe"))
