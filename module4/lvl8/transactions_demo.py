"""Транзакція (слайд 7): видача книги = мінус примірник у books + запис у loans. Або обидва, або нічого.

Працює лише на replica set (Docker з --replSet, Atlas). На одиночному сервері:
OperationFailure: Transaction numbers are only allowed on a replica set member or mongos.
Запуск: python transactions_demo.py
"""

import asyncio
from datetime import UTC, datetime

from pymongo import AsyncMongoClient, ReturnDocument

from config import settings

TITLE = "Місто"


async def lend(client: AsyncMongoClient, user: str, fail_after_first_write: bool = False) -> None:
    db = client[settings.mongo_db]
    # У PyMongo Async: start_session() без await, а start_transaction() з await
    async with client.start_session() as session:  # noqa: SIM117  два блоки, як на слайді
        async with await session.start_transaction():
            book = await db["books"].find_one_and_update(
                {"title": TITLE, "copies": {"$gt": 0}},
                {"$inc": {"copies": -1}},
                session=session,
                return_document=ReturnDocument.AFTER,
            )
            if book is None:
                raise ValueError("немає вільних примірників")
            if fail_after_first_write:
                raise RuntimeError("збій між двома записами")
            await db["loans"].insert_one(
                {"book_id": book["_id"], "user": user, "at": datetime.now(UTC)}, session=session
            )
        # вийшли з блоку без винятку = commit; виняток усередині = abort, обидва записи скасовано


async def show(client: AsyncMongoClient, label: str) -> None:
    db = client[settings.mongo_db]
    book = await db["books"].find_one({"title": TITLE})
    loans = await db["loans"].count_documents({"book_id": book["_id"]})
    print(f"{label}: copies={book.get('copies')}, loans={loans}")


async def main() -> None:
    client = AsyncMongoClient(settings.mongo_uri)
    db = client[settings.mongo_db]
    # Гнучка схема: поля copies у книг не було, просто додаємо його цій одній книзі
    await db["books"].update_one({"title": TITLE}, {"$set": {"copies": 2}})
    await db["loans"].delete_many({})
    await show(client, "старт")

    await lend(client, "olia")
    await show(client, "olia взяла")

    try:
        await lend(client, "petro", fail_after_first_write=True)
    except RuntimeError as e:
        print("petro:", e)
    await show(client, "після збою (copies не зменшився)")

    await lend(client, "ira")
    try:
        await lend(client, "max")
    except ValueError as e:
        print("max:", e)
    await show(client, "кінець")
    await client.close()


if __name__ == "__main__":
    asyncio.run(main())
