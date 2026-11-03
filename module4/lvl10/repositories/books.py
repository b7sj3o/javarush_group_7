from collections.abc import Sequence

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from models import Author, Book
from schemas import BookFilter


class AuthorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_name(self, name: str) -> Author | None:
        stmt = select(Author).where(func.lower(Author.name) == name.lower())
        return await self.session.scalar(stmt)

    def add(self, author: Author) -> None:
        self.session.add(author)


class BookRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, book_id: int) -> Book | None:
        return await self.session.get(Book, book_id)

    async def list(self, filters: BookFilter) -> Sequence[Book]:
        stmt = select(Book)
        if filters.author:
            # any(): «є хоч один автор, у якого…». SQL: WHERE EXISTS (... authors_books_table JOIN authors ...).
            # Без JOIN книга з двома авторами не повториться у видачі двічі.
            stmt = stmt.where(Book.authors.any(func.lower(Author.name).contains(filters.author.lower())))
        if filters.q:
            stmt = stmt.where(func.lower(Book.title).contains(filters.q.lower()))
        if filters.genre:
            stmt = stmt.where(Book.genre == filters.genre)
        if filters.available is not None:
            stmt = stmt.where(Book.available == filters.available)
        if filters.year_from is not None:
            stmt = stmt.where(Book.year >= filters.year_from)
        if filters.year_to is not None:
            stmt = stmt.where(Book.year <= filters.year_to)
        stmt = stmt.order_by(getattr(Book, filters.sort), Book.id).offset(filters.offset).limit(filters.limit)
        result = await self.session.scalars(stmt)
        return result.all()

    async def find_duplicate(self, title: str, author_names: Sequence[str]) -> Book | None:
        """Книга з такою самою назвою, у якої є хоч один із цих авторів."""
        # Sequence, а не list: усередині класу ім'я list уже зайняте методом list() вище
        names = [name.lower() for name in author_names]
        stmt = select(Book).where(
            func.lower(Book.title) == title.lower(),
            Book.authors.any(func.lower(Author.name).in_(names)),
        )
        return await self.session.scalar(stmt)

    def add(self, book: Book) -> None:
        self.session.add(book)

    async def delete(self, book: Book) -> None:
        await self.session.delete(book)
