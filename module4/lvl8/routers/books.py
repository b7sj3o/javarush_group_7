from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from schemas import (
    BookCreate,
    BookFilter,
    BookOut,
    BookShort,
    BookUpdate,
    Review,
    ReviewCreate,
)
from services.books import BookServiceDep

router = APIRouter(prefix="/books", tags=["books"])

BookId = Annotated[str, Path(description="ObjectId книги, 24 hex-символи", examples=["6ae0c43ef72a1add3684b6d6"])]


@router.get("", response_model=list[BookShort])
async def list_books(filters: Annotated[BookFilter, Query()], service: BookServiceDep):
    return await service.list(filters)


@router.get("/{book_id}", response_model=BookOut)
async def get_book(book_id: BookId, service: BookServiceDep):
    return await service.get_or_404(book_id)


@router.post("", response_model=BookOut, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookCreate, service: BookServiceDep):
    return await service.create(data)


@router.patch("/{book_id}", response_model=BookOut)
async def update_book(book_id: BookId, data: BookUpdate, service: BookServiceDep):
    return await service.update(book_id, data)


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: BookId, service: BookServiceDep) -> None:
    await service.delete(book_id)


@router.post("/{book_id}/reviews", response_model=Review, status_code=status.HTTP_201_CREATED)
async def add_review(book_id: BookId, data: ReviewCreate, service: BookServiceDep):
    return await service.add_review(book_id, data)
