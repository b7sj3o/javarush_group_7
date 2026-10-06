import asyncio
import time
from itertools import count
from typing import Annotated, Literal

import httpx
from fastapi import FastAPI, HTTPException, Query, status
from pydantic import BaseModel, Field


app = FastAPI()


class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1450, le=2100)
    available: bool = True


class Book(BookCreate):
    id: int


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1450, le=2100)
    available: bool | None = None
    
    
books_db: dict[int, Book] = {
    1: Book(id=1, title="Кобзар", author="Тарас Шевченко", year=1840),
    2: Book(id=2, title="Захар Беркут", author="Іван Франко", year=1883),
    3: Book(id=3, title="Лісова пісня", author="Леся Українка", year=1911),
    4: Book(id=4, title="Місто", author="Валер'ян Підмогильний", year=1928),
    5: Book(id=5, title="Тигролови", author="Іван Багряний", year=1944, available=False),
    6: Book(id=6, title="Сад Гетсиманський", author="Іван Багряний", year=1950),
}
id_seq = count(len(books_db) + 1)


def get_book_or_404(book_id: int) -> Book:
    book = books_db.get(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з id={book_id} не знайдено",
        )
    return book


@app.get("/books", response_model=list[Book], tags=["books"])
async def list_books(
    author: str | None = None,
    q: Annotated[str | None, Query(min_length=2, description="Пошук у назві")] = None,
    available: bool | None = None,
    sort: Literal["id", "title", "year"] = "id",
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=50)] = 10,
):
    books = list(books_db.values())
    if author:
        books = [b for b in books if author.lower() in b.author.lower()]
    if q:
        books = [b for b in books if q.lower() in b.title.lower()]
    if available is not None:
        books = [b for b in books if b.available == available]
    books.sort(key=lambda b: getattr(b, sort))
    return books[offset : offset + limit]


@app.get("/books/stats", tags=["books"])
async def books_stats():
    years = [b.year for b in books_db.values()]
    return {"count": len(books_db), "oldest": min(years), "newest": max(years)}


@app.get("/books/{book_id}", response_model=Book, tags=["books"])
async def get_book(book_id: int):
    return get_book_or_404(book_id)


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["books"])
async def create_book(data: BookCreate):
    for book in books_db.values():
        if book.title.lower() == data.title.lower() and book.author.lower() == data.author.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "duplicate", "message": "Така книга вже є", "existing_id": book.id},
            )
    book = Book(id=next(id_seq), **data.model_dump())
    books_db[book.id] = book
    return book


@app.put("/books/{book_id}", response_model=Book, tags=["books"])
async def replace_book(book_id: int, data: BookCreate):
    get_book_or_404(book_id)
    book = Book(id=book_id, **data.model_dump())
    books_db[book_id] = book
    return book


@app.patch("/books/{book_id}", response_model=Book, tags=["books"])
async def update_book(book_id: int, data: BookUpdate):
    book = get_book_or_404(book_id)
    changes = data.model_dump(exclude_none=True)    # лише поля, які клієнт заповнив
    updated = book.model_copy(update=changes)
    books_db[book_id] = updated
    return updated


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["books"])
async def delete_book(book_id: int):
    get_book_or_404(book_id)
    del books_db[book_id]