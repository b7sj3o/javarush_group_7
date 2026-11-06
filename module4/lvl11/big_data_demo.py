"""Скільки пам'яті їсть прочитання 200 тис. замовлень. Запуск: python big_data_demo.py all | partitions | stream"""

import asyncio
import sys
import time
import tracemalloc

from sqlalchemy import select

from database import async_session_maker, engine
from models import Order


async def read_all(session) -> int:
    orders = (await session.scalars(select(Order))).all()  # усе в список разом
    return len(orders)


async def read_partitions(session) -> int:
    # Як на слайді: execute() + partitions(). Результат уже повністю в пам'яті, пачки лише нарізають його
    result = await session.execute(select(Order))
    suma = 0
    for batch in result.scalars().partitions(1000):
        print(len(batch))
        suma += len(batch)
        


async def read_stream(session) -> int:
    # stream_scalars + yield_per: курсор на сервері, у пам'яті не більше 1000 об'єктів за раз
    stmt = select(Order).execution_options(yield_per=1000)
    count = 0
    async for _order in await session.stream_scalars(stmt):
        print(_order)
        count += 1
    return count


async def main(mode: str) -> None:
    read = {"all": read_all, "partitions": read_partitions, "stream": read_stream}[mode]
    tracemalloc.start()
    started = time.perf_counter()
    async with async_session_maker() as session:
        count = await read(session)
    _, peak = tracemalloc.get_traced_memory()
    print(f"{mode}: {count} рядків, пік пам'яті {peak / 1024 / 1024:.0f} МБ, {time.perf_counter() - started:.1f} с")
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main(sys.argv[1] if len(sys.argv) > 1 else "stream"))
