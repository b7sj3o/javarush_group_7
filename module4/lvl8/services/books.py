from collections.abc import Sequence
from datetime import UTC, datetime
from typing import Annotated, Any

from bson import ObjectId
from fastapi import Depends

from database import DbDep
from exceptions import ConflictError, NotFoundError
from repositories.books import BookRepository
from schemas import BookCreate, BookFilter, BookUpdate, ReviewCreate


def parse_id(book_id: str) -> ObjectId:
    # «abc» не може бути ObjectId; для клієнта це та сама неіснуюча книга, тому 404, а не 500
    if not ObjectId.is_valid(book_id):
        raise NotFoundError(f"Книгу з id={book_id} не знайдено")
    return ObjectId(book_id)


class BookService:
    def __init__(self, db: DbDep):
        self.books = BookRepository(db)

    async def get_or_404(self, book_id: str) -> dict[str, Any]:
        book = await self.books.get(parse_id(book_id))
        if book is None:
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")
        return book

    async def list(self, filters: BookFilter) -> Sequence[dict[str, Any]]:
        return await self.books.list(filters)

    async def create(self, data: BookCreate) -> dict[str, Any]:
        duplicate = await self.books.find_duplicate(data.title, [a.name for a in data.authors])
        if duplicate is not None:
            raise ConflictError({"code": "duplicate", "message": "Така книга вже є", "existing_id": str(duplicate["_id"])})
        # Документ = словник. Pydantic уже все перевірив, тож просто model_dump() і дописуємо службові поля.
        # Дати тільки datetime: тип date pymongo не збереже (InvalidDocument: cannot encode object)
        doc = data.model_dump() | {"added_at": datetime.now(UTC), "reviews": []}
        doc["_id"] = await self.books.insert(doc)
        return doc

    async def update(self, book_id: str, data: BookUpdate) -> dict[str, Any]:
        fields = data.model_dump(exclude_unset=True)  # лише те, що прийшло в запиті
        if not fields:
            return await self.get_or_404(book_id)
        book = await self.books.update(parse_id(book_id), fields)
        if book is None:
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")
        return book

    async def delete(self, book_id: str) -> None:
        if not await self.books.delete(parse_id(book_id)):
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")

    async def add_review(self, book_id: str, data: ReviewCreate) -> dict[str, Any]:
        review = data.model_dump() | {"created_at": datetime.now(UTC)}
        if not await self.books.add_review(parse_id(book_id), review):
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")
        return review

    async def genre_stats(self) -> Sequence[dict[str, Any]]:
        return await self.books.genre_stats()

    async def top_rated(self, min_reviews: int, limit: int) -> Sequence[dict[str, Any]]:
        return await self.books.top_rated(min_reviews, limit)


BookServiceDep = Annotated[BookService, Depends()]
