from typing import Annotated, AsyncIterator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from config import settings


# Створюємо асинхронний engine
engine = create_async_engine(settings.database_url, echo=settings.debug)

# Фабрика для створення асинхронних сесій
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Базовий клас для всіх наших моделей
class Base(DeclarativeBase):
    pass


async def get_async_session() -> AsyncIterator[AsyncSession]:
    """Одна сесія на запит: відкривається перед ендпоінтом і закривається після відповіді."""
    async with async_session_maker() as session:
        yield session
        

SessionDep = Annotated[AsyncSession, Depends(get_async_session)]