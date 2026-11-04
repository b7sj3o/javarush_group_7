from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, HTTPException, Path, Query, status
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

from dependencies import AdminUser, ManagerUser
from models import ACTIVE_STATUSES, Book, BookCreate, BookUpdate, Genre, book_seq, books_db, orders_db

router = APIRouter(prefix="/books", tags=["books"])

BookId = Annotated[int, Path(ge=1, description="Номер книги")]


def get_book_or_404(book_id: int) -> Book:
    book = books_db.get(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з id={book_id} не знайдено",
        )
    return book


class BookFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author: str | None = None
    q: str | None = Field(default=None, min_length=2, description="Пошук у назві")
    genre: Genre | None = None
    available: bool | None = None
    year_from: int | None = Field(default=None, ge=1450)
    year_to: int | None = Field(default=None, le=2100)
    sort: Literal["id", "title", "year"] = "id"
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)

    @model_validator(mode="after")
    def years_in_order(self):
        if self.year_from is not None and self.year_to is not None and self.year_from > self.year_to:
            raise ValueError("year_from не може бути більшим за year_to")
        return self


# ---------- Читання: усім, без токена ----------

@router.get("", response_model=list[Book])
async def list_books(filters: Annotated[BookFilter, Query()]):
    books = list(books_db.values())
    if filters.author:
        books = [b for b in books if filters.author.lower() in b.author.name.lower()]
    if filters.q:
        books = [b for b in books if filters.q.lower() in b.title.lower()]
    if filters.genre:
        books = [b for b in books if b.genre == filters.genre]
    if filters.available is not None:
        books = [b for b in books if b.available == filters.available]
    if filters.year_from is not None:
        books = [b for b in books if b.year >= filters.year_from]
    if filters.year_to is not None:
        books = [b for b in books if b.year <= filters.year_to]
    books.sort(key=lambda b: getattr(b, filters.sort))
    return books[filters.offset : filters.offset + filters.limit]


@router.get("/{book_id}", response_model=Book)
async def get_book(book_id: BookId):
    return get_book_or_404(book_id)


# ---------- Зміна: manager / admin ----------

@router.post("", response_model=Book, status_code=status.HTTP_201_CREATED)
async def create_book(data: BookCreate, user: ManagerUser):
    for book in books_db.values():
        if book.title.lower() == data.title.lower() and book.author.name.lower() == data.author.name.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "duplicate", "message": "Така книга вже є", "existing_id": book.id},
            )
    book = Book(id=next(book_seq), added_at=date.today(), **data.model_dump())
    books_db[book.id] = book
    return book


@router.put("/{book_id}", response_model=Book)
async def replace_book(book_id: BookId, data: BookCreate, user: ManagerUser):
    old = get_book_or_404(book_id)
    payload = data.model_dump()
    if "available" not in data.model_fields_set:      # не передали -> лишаємо як було
        payload["available"] = old.available
    book = Book(id=book_id, added_at=old.added_at, **payload)
    books_db[book_id] = book
    return book


@router.patch("/{book_id}", response_model=Book)
async def update_book(book_id: BookId, data: BookUpdate, user: ManagerUser):
    book = get_book_or_404(book_id)
    changes = data.model_dump(exclude_unset=True)
    merged = {**book.model_dump(), **changes}
    try:
        updated = Book.model_validate(merged)      # повна перевірка, разом із model_validator
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))
    books_db[book_id] = updated
    return updated


# ---------- Видалення: лише admin ----------

@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: BookId, admin: AdminUser) -> None:
    get_book_or_404(book_id)
    if any(o.book_id == book_id and o.status in ACTIVE_STATUSES for o in orders_db.values()):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="У книги є активні замовлення (new, confirmed, issued)",
        )
    del books_db[book_id]
