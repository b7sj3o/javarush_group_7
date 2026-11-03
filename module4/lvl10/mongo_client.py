from fastapi import Request
from pymongo.asynchronous.database import AsyncDatabase

from config import settings

def get_mongo_db(request: Request):
    return request.app.state.mongo[settings.mongo_db]


async def init_mongo(db: AsyncDatabase) -> None:
    # Один відгук від одного юзера на книгу: повторний insert дасть DuplicateKeyError -> 409
    await db["reviews"].create_index([("book_id", 1), ("user_id", 1)], unique=True)
    # TTL-індекс: документ видаляється сам, коли від "at" минуло EVENTS_TTL_SECONDS
    await db["events"].create_index("at", expireAfterSeconds=60*60*24*30)
    await db["events"].create_index([("type", 1), ("at", -1)])
