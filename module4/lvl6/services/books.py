from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from database import SessionDep
from exceptions import ConflictError, NotFoundError
from models import Author, Book
from repositories.books import AuthorRepository, BookRepository
from repositories.orders import OrderRepository
from schemas import AuthorSchema, BookCreate, BookFilter, BookUpdate


class BookService:
    def __init__(self, session: SessionDep):
        self.session = session
        self.books = BookRepository(session)
        self.authors = AuthorRepository(session)
        self.orders = OrderRepository(session)
        
        
    async def list(self, filters: BookFilter) -> list[Book]:
        return await self.books.list(filters)
    
    
    
BookServiceDep = Annotated[BookService, Depends()]