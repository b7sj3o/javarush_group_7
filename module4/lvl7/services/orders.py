from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends

from database import SessionDep
from exceptions import ConflictError, NotFoundError
from models import ALLOWED_TRANSITIONS, Order, OrderStatus, Role, User
from repositories.books import BookRepository
from repositories.orders import OrderRepository
from schemas import OrderCreate, OrderFilter, OrderUpdate


class OrderService:
    def __init__(self, session: SessionDep):
        self.session = session
        self.orders = OrderRepository(session)
        self.books = BookRepository(session)

    async def get_or_404(self, order_id: int) -> Order:
        order = await self.orders.get(order_id)
        if order is None:
            raise NotFoundError(f"Замовлення з id={order_id} не знайдено")
        return order

    async def get_visible(self, order_id: int, user: User) -> Order:
        """reader бачить лише власні; чуже для нього виглядає як неіснуюче (404)."""
        order = await self.get_or_404(order_id)
        if user.role == Role.READER and order.customer_id != user.id:
            raise NotFoundError(f"Замовлення з id={order_id} не знайдено")
        return order

    async def create(self, data: OrderCreate, user: User) -> Order:
        book = await self.books.get(data.book_id)
        if book is None:
            raise NotFoundError(f"Книгу з id={data.book_id} не знайдено")
        if not book.available:
            raise ConflictError("Книга зараз недоступна")
        order = Order(
            customer_id=user.id,
            book_id=book.id,
            delivery=data.delivery.model_dump(),
            delivery_date=data.delivery_date,
        )
        self.orders.add(order)
        book.available = False  # дві зміни, один commit: або обидві в базі, або жодної
        await self.session.commit()
        await self.session.refresh(order)  # created_at поставила база, підтягуємо його
        return order

    async def list(self, filters: OrderFilter) -> Sequence[Order]:
        return await self.orders.list(filters)

    async def update(self, order_id: int, data: OrderUpdate, user: User) -> Order:
        order = await self.get_or_404(order_id)
        if order.customer_id != user.id:  # чуже -> 404 (для будь-якої ролі)
            raise NotFoundError(f"Замовлення з id={order_id} не знайдено")
        if order.status != OrderStatus.NEW:
            raise ConflictError("Редагувати можна лише замовлення зі статусом new")
        if data.delivery is not None:
            order.delivery = data.delivery.model_dump()  # JSON-поле: присвоюємо новий dict, а не міняємо старий
        if data.delivery_date is not None:
            order.delivery_date = data.delivery_date
        await self.session.commit()
        return order

    async def _change_status(self, order: Order, new_status: OrderStatus) -> Order:
        """Єдине місце, де міняється статус: перевірка переходу + звільнення книги."""
        if new_status not in ALLOWED_TRANSITIONS[order.status]:
            raise ConflictError(f"Перехід {order.status.value} → {new_status.value} недозволений")
        order.status = new_status
        if new_status in (OrderStatus.CANCELLED, OrderStatus.RETURNED):
            book = await self.books.get(order.book_id)
            if book is not None:
                book.available = True
        await self.session.commit()
        return order

    async def cancel(self, order_id: int, user: User) -> Order:
        order = await self.get_visible(order_id, user)
        return await self._change_status(order, OrderStatus.CANCELLED)

    async def set_status(self, order_id: int, new_status: OrderStatus) -> Order:
        order = await self.get_or_404(order_id)
        return await self._change_status(order, new_status)

    async def delete(self, order_id: int) -> None:
        order = await self.get_or_404(order_id)
        if order.status not in (OrderStatus.CANCELLED, OrderStatus.RETURNED):
            raise ConflictError("Видалити можна лише замовлення зі статусом cancelled або returned")
        await self.orders.delete(order)
        await self.session.commit()


OrderServiceDep = Annotated[OrderService, Depends()]
