from typing import Annotated

from fastapi import Depends, Request
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase

from config import settings


def create_client() -> AsyncMongoClient:
    return AsyncMongoClient(settings.mongo_uri)


def get_db(request: Request) -> AsyncDatabase:
    return request.app.state.mongo[settings.mongo_db]


DbDep = Annotated[AsyncDatabase, Depends(get_db)]
