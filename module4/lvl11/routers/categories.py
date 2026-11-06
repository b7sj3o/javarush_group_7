from fastapi import APIRouter
from sqlalchemy import delete, select

from database import SessionDep, get_or_404
from models import Category
from schemas import CategoryCreate, CategoryRead

router = APIRouter()


@router.post("", response_model=CategoryRead, status_code=201)
async def create_category(data: CategoryCreate, session: SessionDep):
    async with session.begin():
        category = Category(name=data.name)
        session.add(category)
    return category


@router.get("", response_model=list[CategoryRead])
async def list_categories(session: SessionDep):
    return (await session.scalars(select(Category).order_by(Category.id))).all()


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: int, session: SessionDep):
    return await get_or_404(session, Category, category_id)


@router.put("/{category_id}", response_model=CategoryRead)
async def update_category(category_id: int, data: CategoryCreate, session: SessionDep):
    async with session.begin():
        category = await get_or_404(session, Category, category_id)
        category.name = data.name
    return category


@router.delete("/{category_id}", status_code=204)
async def delete_category(category_id: int, session: SessionDep):
    """Є товари в категорії -> зовнішній ключ не дасть видалити -> 409."""
    async with session.begin():
        await get_or_404(session, Category, category_id)
        await session.execute(delete(Category).where(Category.id == category_id))
