"""Таблиці й стартові дані для тестів (SQLite у пам'яті).

У справжній базі таблиці створює міграція initial, а дані кладе міграція seed data.
"""

from datetime import date
from functools import cache

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncEngine, async_sessionmaker

from database import Base
from models import Author, Book, Genre, Role, User
from security import hash_password


@cache
def _hashed(password: str) -> str:
    # argon2 навмисно повільний (~50 мс). Тести перебудовують базу перед кожним тестом,
    # тож хешуємо кожен стартовий пароль один раз на процес.
    return hash_password(password)


def _seed_objects() -> list:
    shevchenko = Author(name="Тарас Шевченко", born=1814)
    franko = Author(name="Іван Франко", born=1856)
    ukrainka = Author(name="Леся Українка", born=1871)
    pidmohylny = Author(name="Валер'ян Підмогильний", born=1901)
    bahrianyi = Author(name="Іван Багряний", born=1906)
    return [
        User(name="Адмін", email="admin@library.ua", hashed_password=_hashed("admin12345"), role=Role.ADMIN),
        User(name="Менеджер", email="manager@library.ua", hashed_password=_hashed("manager12345"), role=Role.MANAGER),
        User(name="Оля", email="olia@example.com", hashed_password=_hashed("secret123")),
        # щоб перевірити 403 для деактивованого
        User(name="Неактивний", email="off@example.com", hashed_password=_hashed("secret123"), is_active=False),
        Book(
            title="Кобзар",
            authors=[shevchenko],
            year=1840,
            genre=Genre.POETRY,
            isbn="9789660301016",
            added_at=date(2026, 10, 1),
        ),
        Book(title="Захар Беркут", authors=[franko], year=1883, genre=Genre.HISTORY, added_at=date(2026, 10, 1)),
        Book(title="Лісова пісня", authors=[ukrainka], year=1911, genre=Genre.DRAMA, added_at=date(2026, 10, 1)),
        Book(title="Місто", authors=[pidmohylny], year=1928, genre=Genre.NOVEL, added_at=date(2026, 10, 2)),
        Book(
            title="Тигролови",
            authors=[bahrianyi],
            year=1944,
            genre=Genre.NOVEL,
            available=False,
            added_at=date(2026, 10, 2),
        ),
        Book(
            title="Сад Гетсиманський",
            authors=[bahrianyi],
            year=1950,
            genre=Genre.NOVEL,
            isbn="9789660312227",
            added_at=date(2026, 10, 3),
        ),
    ]


async def init_db(engine: AsyncEngine) -> None:
    """Створює таблиці, яких ще немає, і заповнює порожню базу."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # create_all синхронний, тому run_sync

    session_maker = async_sessionmaker(engine, expire_on_commit=False)
    async with session_maker() as session:
        if await session.scalar(select(User.id).limit(1)) is not None:
            return  # база вже заповнена: перезапуск сервера нічого не дублює
        session.add_all(_seed_objects())
        await session.commit()
