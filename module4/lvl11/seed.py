"""Перестворює таблиці й наповнює базу магазину. Запуск: python seed.py (~15 с, база стирається!)."""

import asyncio
import random
from datetime import UTC, datetime, timedelta
from decimal import Decimal

from sqlalchemy import insert, text

from database import Base, async_session_maker, engine
from models import Category, Order, OrderItem, Product, Profile, Tag, User, product_tags

USERS = 1_000
ORDERS = 200_000
CHUNK = 20_000

CATEGORIES = ["Книги", "Електроніка", "Одяг", "Дім", "Спорт"]
TAGS = ["новинка", "знижка", "хіт", "подарунок", "еко", "преміум", "україна", "лімітовано"]
CITIES = ["Київ", "Львів", "Одеса", "Харків", "Дніпро", "Вінниця"]

PRODUCTS = 50
LIMITED_PRODUCT_ID = PRODUCTS + 1  # товар для демо гонки: id 51, залишок 5


def price() -> Decimal:
    return Decimal(random.randrange(5_000, 500_000)) / 100


async def seed() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    random.seed(42)
    products = [
        {"name": f"Товар {i}", "price": price(), "stock": random.randint(10, 500),
         "category_id": random.randint(1, len(CATEGORIES))}
        for i in range(1, PRODUCTS + 1)
    ]
    products.append({"name": "Лімітована серія", "price": Decimal("100.00"), "stock": 5, "category_id": 1})
    links = [
        {"product_id": i, "tag_id": t}
        for i in range(1, PRODUCTS + 1)
        for t in random.sample(range(1, len(TAGS) + 1), k=3)
    ]
    users = [
        {"name": f"Юзер {i}", "email": f"user{i}@example.com", "age": random.randint(18, 70),
         "balance": Decimal("10000.00")}
        for i in range(1, USERS + 1)
    ]
    profiles = [{"user_id": i, "city": random.choice(CITIES)} for i in range(1, USERS + 1)]

    now = datetime.now(UTC).replace(tzinfo=None)
    orders, items = [], []
    for order_id in range(1, ORDERS + 1):
        product = random.randint(1, PRODUCTS)
        quantity = random.randint(1, 3)
        unit_price = products[product - 1]["price"]
        orders.append({"user_id": random.randint(1, USERS), "total": unit_price * quantity,
                       "created_at": now - timedelta(minutes=random.randint(0, 525_600))})
        items.append({"order_id": order_id, "product_id": product, "quantity": quantity, "price": unit_price})

    async with async_session_maker() as session:
        await session.execute(insert(Category), [{"name": n} for n in CATEGORIES])
        await session.execute(insert(Tag), [{"name": n} for n in TAGS])
        await session.execute(insert(Product), products)
        await session.execute(insert(product_tags), links)
        await session.execute(insert(User), users)
        await session.execute(insert(Profile), profiles)
        # Пачками: id йдуть підряд 1..ORDERS, тому order_id в items збігається
        for start in range(0, ORDERS, CHUNK):
            await session.execute(insert(Order), orders[start:start + CHUNK])
            await session.execute(insert(OrderItem), items[start:start + CHUNK])
        await session.commit()

    async with engine.connect() as conn:
        await conn.execution_options(isolation_level="AUTOCOMMIT")
        await conn.execute(text("ANALYZE"))  # оновити статистику для планувальника: інакше EXPLAIN бреше
    await engine.dispose()
    print(f"Готово: {USERS} юзерів, {PRODUCTS + 1} товарів, {ORDERS} замовлень")


if __name__ == "__main__":
    asyncio.run(seed())
