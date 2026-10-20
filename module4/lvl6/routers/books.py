from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from dependencies import AdminUser, ManagerUser
from schemas import BookCreate, BookFilter, BookOut, BookUpdate
from services.books import BookServiceDep

router = APIRouter(prefix="/books", tags=["books"])

BookId = Annotated[int, Path(ge=1, description="Номер книги")]


# ---------- Читання: усім, без токена ----------


@router.get("", response_model=list[BookOut])
async def list_books(filters: Annotated[BookFilter, Query()], service: BookServiceDep):
    return await service.list(filters)


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: BookId, service: BookServiceDep):
    return await service.get_or_404(book_id)


# ---------- Зміна: manager / admin ----------


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookCreate, user: ManagerUser, service: BookServiceDep):
    return await service.create(data)


@router.put("/{book_id}", response_model=BookOut)
async def replace_book(book_id: BookId, data: BookCreate, user: ManagerUser, service: BookServiceDep):
    return await service.replace(book_id, data)


@router.patch("/{book_id}", response_model=BookOut)
async def update_book(book_id: BookId, data: BookUpdate, user: ManagerUser, service: BookServiceDep):
    return await service.update(book_id, data)


# ---------- Видалення: лише admin ----------


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: BookId, admin: AdminUser, service: BookServiceDep) -> None:
    await service.delete(book_id)
