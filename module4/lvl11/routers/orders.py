from decimal import Decimal

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database import SessionDep, get_or_404
from models import Order, OrderItem, Product, User
from schemas import OrderCreate, OrderCreated, OrderDetail, OrderRead

router = APIRouter()


async def _add_order(session: AsyncSession, data: OrderCreate, price: Decimal) -> Order:
    order = Order(user_id=data.user_id, total=price * data.quantity)
    session.add(order)

    await session.flush() 

    session.add(OrderItem(order_id=order.id, product_id=data.product_id, quantity=data.quantity, price=price))
    return order

@router.post("", response_model=OrderCreated, status_code=201)
async def create_order(data: OrderCreate, session: SessionDep):
    async with session.begin():
        await get_or_404(session, User, data.user_id)

        product = await session.get(Product, data.product_id, with_for_update=True)

        if product is None:
            raise HTTPException(status_code=404, detail="Товар не знайдений")

        if product.stock < data.quantity:
            raise HTTPException(status_code=409, detail="Недостатньо товару на складі")

        product.stock -= data.quantity

        order = await _add_order(session, data, product.price)
    return OrderCreated(order_id=order.id, total=order.total, stock_left=product.stock)


@router.get("", response_model=list[OrderRead])
async def list_orders(session: SessionDep, limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    return (await session.scalars(select(Order).order_by(Order.id).limit(limit).offset(offset))).all()


@router.get("/{order_id}", response_model=OrderDetail)
async def get_order(order_id: int, session: SessionDep):
    order = await session.get(Order, order_id, options=[selectinload(Order.items)])
    if order is None:
        raise HTTPException(status_code=404, detail=f"Order {order_id} не знайдено")
    return order


@router.delete("/{order_id}", status_code=204)
async def delete_order(order_id: int, session: SessionDep):
    """Скасування: залишок повертається на склад, усе в одній транзакції."""
    async with session.begin():
        await get_or_404(session, Order, order_id)
        items = (await session.scalars(select(OrderItem).where(OrderItem.order_id == order_id))).all()
        for item in items:
            product = await session.get(Product, item.product_id, with_for_update=True)
            product.stock += item.quantity
        await session.execute(delete(OrderItem).where(OrderItem.order_id == order_id))
        await session.execute(delete(Order).where(Order.id == order_id))
