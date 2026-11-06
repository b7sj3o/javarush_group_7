from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from database import SessionDep, get_or_404
from models import Product, Tag, product_tags
from schemas import ProductCreate, ProductShort, ProductUpdate, ProductRead

router = APIRouter()


async def _load_tags(session: AsyncSession, tag_ids: list[int]) -> list[Tag]:
    tags = (await session.scalars(select(Tag).where(Tag.id.in_(tag_ids)))).all()
    if len(tags) != len(set(tag_ids)):
        raise HTTPException(status_code=404, detail="Якогось тегу не знайдено")
    return list(tags)


@router.post("", response_model=ProductShort, status_code=201)
async def create_product(data: ProductCreate, session: SessionDep):
    async with session.begin():
        tags = await _load_tags(session, data.tag_ids)
        product = Product(**data.model_dump(exclude={"tag_ids"}), tags=tags)
        session.add(product)
    return product


@router.get("", response_model=list[ProductShort])
async def list_products(session: SessionDep, limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    return (await session.scalars(select(Product).order_by(Product.id).limit(limit).offset(offset))).all()


@router.get("/{product_id}", response_model=ProductRead)
async def get_product(product_id: int, session: SessionDep):
    return await session.scalar(
        select(Product)
        .where(Product.id == product_id)
        .options(
            joinedload(Product.category),
            selectinload(Product.tags)
        )
    )


@router.patch("/{product_id}", response_model=ProductShort)
async def update_product(product_id: int, data: ProductUpdate, session: SessionDep):
    async with session.begin():
        product = await session.get(Product, product_id, options=[selectinload(Product.tags)])
        if product is None:
            raise HTTPException(status_code=404, detail=f"Product {product_id} не знайдено")
        for field, value in data.model_dump(exclude_none=True, exclude={"tag_ids"}).items():
            setattr(product, field, value)
        if data.tag_ids is not None:
            product.tags = await _load_tags(session, data.tag_ids)
    return product


@router.delete("/{product_id}", status_code=204)
async def delete_product(product_id: int, session: SessionDep):
    """Товар є в замовленнях -> зовнішній ключ не дасть видалити -> 409."""
    async with session.begin():
        await get_or_404(session, Product, product_id)
        await session.execute(delete(product_tags).where(product_tags.c.product_id == product_id))
        await session.execute(delete(Product).where(Product.id == product_id))
