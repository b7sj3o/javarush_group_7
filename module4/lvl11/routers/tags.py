from fastapi import APIRouter
from sqlalchemy import delete, select

from database import SessionDep, get_or_404
from models import Tag, product_tags
from schemas import TagCreate, TagRead

router = APIRouter()


@router.post("", response_model=TagRead, status_code=201)
async def create_tag(data: TagCreate, session: SessionDep):
    async with session.begin():
        tag = Tag(name=data.name)
        session.add(tag)
    return tag


@router.get("", response_model=list[TagRead])
async def list_tags(session: SessionDep):
    return (await session.scalars(select(Tag).order_by(Tag.id))).all()


@router.get("/{tag_id}", response_model=TagRead)
async def get_tag(tag_id: int, session: SessionDep):
    return await get_or_404(session, Tag, tag_id)


@router.put("/{tag_id}", response_model=TagRead)
async def update_tag(tag_id: int, data: TagCreate, session: SessionDep):
    async with session.begin():
        tag = await get_or_404(session, Tag, tag_id)
        tag.name = data.name
    return tag


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(tag_id: int, session: SessionDep):
    """Спершу зв'язки в проміжній таблиці, потім сам тег."""
    async with session.begin():
        await get_or_404(session, Tag, tag_id)
        await session.execute(delete(product_tags).where(product_tags.c.tag_id == tag_id))
        await session.execute(delete(Tag).where(Tag.id == tag_id))
