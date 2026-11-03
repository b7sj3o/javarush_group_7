from collections.abc import Sequence
import json
from typing import Annotated, Any

from fastapi import Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from redis.asyncio import Redis

from dependencies import RedisDep, SessionDep, MongoDep
from exceptions import ConflictError, NotFoundError
from models import Author, Book
from repositories.books import AuthorRepository, BookRepository
from repositories.orders import OrderRepository
from schemas import AuthorSchema, BookCreate, BookFilter, BookOut, BookDetail, BookUpdate

BOOK_CACHE_KEY = "books:{book_id}"
BOOKS_LIST_CACHE_KEY = "books:list:{filters}"


async def invalidate_books(redis: Redis, book_id: int | None = None) -> None:
    """Книга змінилась: її ключ і всі сторінки списку більше не правдиві."""
    keys = [key async for key in redis.scan_iter(match="books:list:*")]
    if book_id is not None:
        keys.append(BOOK_CACHE_KEY.format(book_id=book_id))
    if keys:
        await redis.delete(*keys)


class BookService:
    def __init__(self, session: SessionDep, redis: RedisDep, mongo: MongoDep):
        self.session = session
        self.books = BookRepository(session)
        self.authors = AuthorRepository(session)
        self.orders = OrderRepository(session)
        self.redis = redis
        self.mongo = mongo
        self.cache_key = BOOK_CACHE_KEY
        self.cache_key_many = BOOKS_LIST_CACHE_KEY
        
    
        
    # no cache
    async def get_or_404(self, book_id: int) -> Book:
        book = await self.books.get(book_id)
        if book is None:
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")
        return book

    # with cache
    async def get(self, book_id: int) -> Book:
            book_cache = await self.redis.get(self.cache_key.format(book_id=book_id))
            
            if book_cache:
                return json.loads(book_cache)
            
            book = await self.books.get(book_id)
            book_details = await self.mongo["book_details"].find_one({"_id": book_id}, {"_id": 0})
            book.details = book_details
            print("=======================")
            print(book.details)
            print("=======================")
            
            if book is None:
                raise NotFoundError(f"Книгу з id={book_id} не знайдено")
            
            await self.redis.setex(self.cache_key.format(book_id=book_id), 60*60, BookDetail.model_validate(book, from_attributes=True).model_dump_json())
            
            return book
    

    async def list(self, filters: BookFilter) -> Sequence[Book]:
        # Фільтри в ключі: інакше ?genre=poetry віддав би те, що закешував ?genre=novel
        cache_key = self.cache_key_many.format(filters=filters.model_dump_json(exclude_none=True))
        books_cache = await self.redis.get(cache_key)
        
        if books_cache:
            # return BookOut.model_validate(books_cache)
            return json.loads(books_cache)
        
        books = await self.books.list(filters)
        data = [BookOut.model_validate(book, from_attributes=True).model_dump(mode="json") for book in books]
        await self.redis.setex(cache_key, 60*60, json.dumps(data, ensure_ascii=False))
        
        return books


    async def _get_or_create_author(self, data: AuthorSchema) -> Author:
        author = await self.authors.get_by_name(data.name)
        if author is None:
            author = Author(name=data.name, born=data.born)
            self.authors.add(author)
        return author

    async def _fill(self, book: Book, data: BookCreate) -> None:
        book.title = data.title
        book.year = data.year
        book.genre = data.genre
        book.isbn = data.isbn
        book.pages = data.pages
        book.available = data.available
        # Нові рядки в authors_books_table SQLAlchemy вставить сама: досить присвоїти список.
        # Повтори прибираємо, інакше та сама пара (author_id, book_id) порушить композитний ключ.
        unique = {a.name.lower(): a for a in data.authors}.values()
        book.authors = [await self._get_or_create_author(a) for a in unique]

    async def create(self, data: BookCreate) -> Book:
        duplicate = await self.books.find_duplicate(data.title, [a.name for a in data.authors])
        if duplicate is not None:
            raise ConflictError({"code": "duplicate", "message": "Така книга вже є", "existing_id": duplicate.id})
        book = Book()
        await self._fill(book, data)
        self.books.add(book)
        await self.session.commit()
        await invalidate_books(self.redis)  # нова книга може потрапити в будь-яку сторінку списку
        return book

    async def replace(self, book_id: int, data: BookCreate) -> Book:
        book = await self.get_or_404(book_id)
        await self._fill(book, data)
        await self.session.commit()
        await invalidate_books(self.redis, book_id)
        return book

    async def update(self, book_id: int, data: BookUpdate) -> Book:
        book = await self.get_or_404(book_id)
        current = BookCreate.model_validate(book, from_attributes=True, extra="ignore")
        merged = {**current.model_dump(), **data.model_dump(exclude_none=True)}
        try:
            full = BookCreate.model_validate(merged)  # повна перевірка, разом із model_validator
        except ValidationError as e:
            raise RequestValidationError(e.errors()) from None  # FastAPI віддасть звичайну 422
        await self._fill(book, full)
        await self.session.commit()
        
        await invalidate_books(self.redis, book_id)  # і книга, і всі сторінки списку
        
        return book

    async def delete(self, book_id: int) -> None:
        book = await self.get_or_404(book_id)
        if await self.orders.has_active_for_book(book_id):
            raise ConflictError("У книги є активні замовлення (new, confirmed, issued)")
        # Завершені замовлення видаляємо разом із книгою: один commit, одна транзакція
        await self.orders.delete_for_book(book_id)
        await self.books.delete(book)
        await self.session.commit()
        await invalidate_books(self.redis, book_id)


    async def set_details(self, book_id: int, details: dict[str, Any]) -> dict[str, Any]:
        await self.get_or_404(book_id)
        
        await self.mongo["book_details"].replace_one({"_id": book_id}, details, upsert=True)
        await invalidate_books(self.redis, book_id)
        return details

BookServiceDep = Annotated[BookService, Depends()]
