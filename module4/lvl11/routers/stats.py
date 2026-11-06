from fastapi import APIRouter
from sqlalchemy import func, select

from database import SessionDep
from models import Category, Order, OrderItem, Product, User

router = APIRouter()



@router.get("/summary")
async def stats_summary(session: SessionDep):
    users = await session.scalar(select(func.count(User.id)))
    avg_age = await session.scalar(select(func.avg(User.age)))
    orders = await session.scalar(select(func.count(Order.id)))
    return {"users": users, "avg_age": round(avg_age, 1), "orders": orders}


@router.get("/categories")
async def stats_categories(session: SessionDep):
    """Виручка за категоріями: JOIN + GROUP BY. Кілька стовпців, тому execute, а не scalars."""
    revenue = func.sum(OrderItem.price * OrderItem.quantity).label("revenue")
    stmt = (
        select(Category.name, revenue, func.count(OrderItem.id).label("items"))
        .join(Product, Product.category_id == Category.id)
        .join(OrderItem, OrderItem.product_id == Product.id)
        .group_by(Category.name)
        .order_by(revenue.desc())
    )
    rows = (await session.execute(stmt)).all()
    return [{"category": r.name, "revenue": r.revenue, "items": r.items} for r in rows]


@router.get("/above-average")
async def products_above_average(session: SessionDep):
    """Підзапит: товари, дорожчі за середню ціну."""
    average = select(func.avg(Product.price)).scalar_subquery()
    stmt = select(Product.name, Product.price).where(Product.price > average).order_by(Product.price.desc()).limit(5)
    rows = (await session.execute(stmt)).all()
    return [{"name": r.name, "price": r.price} for r in rows]
