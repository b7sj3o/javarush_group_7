from collections.abc import Sequence

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import ACTIVE_STATUSES, Order
from schemas import OrderFilter


class OrderRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, order_id: int) -> Order | None:
        return await self.session.get(Order, order_id)

    async def list(self, filters: OrderFilter) -> Sequence[Order]:
        stmt = select(Order)
        if filters.status is not None:
            stmt = stmt.where(Order.status == filters.status)
        if filters.book_id is not None:
            stmt = stmt.where(Order.book_id == filters.book_id)
        stmt = stmt.order_by(Order.id).offset(filters.offset).limit(filters.limit)
        result = await self.session.scalars(stmt)
        return result.all()

    async def has_active_for_book(self, book_id: int) -> bool:
        stmt = select(Order.id).where(Order.book_id == book_id, Order.status.in_(ACTIVE_STATUSES)).limit(1)
        return await self.session.scalar(stmt) is not None

    async def delete_for_book(self, book_id: int) -> None:
        await self.session.execute(delete(Order).where(Order.book_id == book_id))

    def add(self, order: Order) -> None:
        self.session.add(order)

    async def delete(self, order: Order) -> None:
        await self.session.delete(order)
