from collections.abc import Sequence
import json
from typing import Annotated

from fastapi import Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from database import SessionDep
from dependencies import RedisDep
from exceptions import ConflictError, NotFoundError
from models import Author, Book
from repositories.books import AuthorRepository, BookRepository
from repositories.orders import OrderRepository
from schemas import AuthorSchema, BookCreate, BookFilter, BookOut, BookUpdate


class BookService:
    def __init__(self, session: SessionDep, redis: RedisDep):
        self.session = session
        self.books = BookRepository(session)
        self.authors = AuthorRepository(session)
        self.orders = OrderRepository(session)
        self.redis = redis
        self.cache_key = "books:{book_id}"
        self.cache_key_many = "books"
        
    
        
    async def get_or_404(self, book_id: int) -> Book:
        book = await self.books.get(book_id)
        if book is None:
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")
        return book

    
    async def get(self, book_id: int) -> Book:
            book_cache = await self.redis.get(self.cache_key.format(book_id=book_id))
            
            if book_cache:
                return json.loads(book_cache)
            
            book = await self.books.get(book_id)
            if book is None:
                raise NotFoundError(f"Книгу з id={book_id} не знайдено")
            
            await self.redis.setex(self.cache_key.format(book_id=book_id), 60*60, BookOut.model_validate(book, from_attributes=True).model_dump_json())
            
            return book
    

    async def list(self, filters: BookFilter) -> Sequence[Book]:
        books_cache = await self.redis.get(self.cache_key_many)
        
        if books_cache:
            # return BookOut.model_validate(books_cache)
            return json.loads(books_cache)
        
        books = await self.books.list(filters)
        data = [BookOut.model_validate(book, from_attributes=True).model_dump(mode="json") for book in books]
        await self.redis.setex(self.cache_key_many, 60*60, json.dumps(data, ensure_ascii=False))
        
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
        return book

    async def replace(self, book_id: int, data: BookCreate) -> Book:
        book = await self.get_or_404(book_id)
        await self._fill(book, data)
        await self.session.commit()
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
        
        await self.redis.delete(self.cache_key.format(book_id=book_id))
        
        return book

    async def delete(self, book_id: int) -> None:
        book = await self.get_or_404(book_id)
        if await self.orders.has_active_for_book(book_id):
            raise ConflictError("У книги є активні замовлення (new, confirmed, issued)")
        # Завершені замовлення видаляємо разом із книгою: один commit, одна транзакція
        await self.orders.delete_for_book(book_id)
        await self.books.delete(book)
        await self.session.commit()


BookServiceDep = Annotated[BookService, Depends()]
