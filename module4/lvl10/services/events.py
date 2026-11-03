from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any

from fastapi import Depends
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.errors import PyMongoError

from dependencies import MongoDep


async def log_event(mongo: AsyncDatabase, event_type: str, user_id: int | None, **data: Any) -> None:
    """Запис у журнал подій. У кожного типу свій набір полів у data: Mongo це дозволяє."""
    try:
        await mongo["events"].insert_one(
            {"type": event_type, "user_id": user_id, "at": datetime.now(UTC), "data": data}
        )
    except PyMongoError as e:
        # Журнал не критичний: замовлення вже збережене в Postgres, тож не валимо через лог увесь запит
        print(f"event {event_type} не записано: {e}")


class EventService:
    def __init__(self, mongo: MongoDep):
        self.events = mongo["events"]

    async def list(self, event_type: str | None, user_id: int | None, limit: int) -> Sequence[dict]:
        query: dict[str, Any] = {}
        if event_type:
            query["type"] = event_type
        if user_id is not None:
            query["user_id"] = user_id
        cursor = self.events.find(query, {"_id": 0}).sort("at", -1).limit(limit)
        return await cursor.to_list()


EventServiceDep = Annotated[EventService, Depends()]
