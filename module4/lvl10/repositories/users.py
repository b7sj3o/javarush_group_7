from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import User


class UserRepository:
    """Лише запити до таблиці users. Жодних HTTP-помилок і жодних commit."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)  # пошук за первинним ключем

    async def get_by_email(self, email: str) -> User | None:
        # lower() з обох боків: email міг бути збережений як Olia@Example.com
        return await self.session.scalar(select(User).where(func.lower(User.email) == email.lower()))

    async def list(self) -> Sequence[User]:
        result = await self.session.scalars(select(User).order_by(User.id))
        return result.all()

    def add(self, user: User) -> None:
        self.session.add(user)
