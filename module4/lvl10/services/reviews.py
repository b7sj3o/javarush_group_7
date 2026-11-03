from datetime import UTC, datetime
from typing import Annotated

from fastapi import Depends
from pymongo.errors import DuplicateKeyError

from dependencies import SessionDep
from dependencies import MongoDep
from exceptions import ConflictError, NotFoundError
from models import User
from repositories.books import BookRepository
from schemas import ReviewCreate
from services.events import log_event


class ReviewService:
    """Відгуки живуть у Mongo, а книги й юзери в Postgres. Зв'язок лише через спільні id."""

    def __init__(self, session: SessionDep, mongo: MongoDep):
        self.books = BookRepository(session)
        self.mongo = mongo
        self.reviews = mongo["reviews"]

    async def _book_exists_or_404(self, book_id: int) -> None:
        # Зовнішнього ключа між базами немає: що книга існує, перевіряємо самі в Postgres
        if await self.books.get(book_id) is None:
            raise NotFoundError(f"Книгу з id={book_id} не знайдено")

    async def add(self, book_id: int, user: User, data: ReviewCreate) -> dict:
        await self._book_exists_or_404(book_id)
        review = {
            "book_id": book_id,  # id з Postgres
            "user_id": user.id,  # id з Postgres
            "user_name": user.name,  # копія імені: показати відгук без запиту в Postgres
            "rating": data.rating,
            "text": data.text,
            "created_at": datetime.now(UTC),
        }
        try:
            await self.reviews.insert_one(review)
        except DuplicateKeyError:  # унікальний індекс (book_id, user_id) з init_mongo
            raise ConflictError("Ви вже залишили відгук на цю книгу") from None
        await log_event(self.mongo, "review_created", user.id, book_id=book_id, rating=data.rating)
        return review

    async def list(self, book_id: int) -> dict:
        await self._book_exists_or_404(book_id)
        reviews = await self.reviews.find({"book_id": book_id}, {"_id": 0}).sort("created_at", -1).to_list()
        # Середню оцінку рахує сама Mongo: агрегація замість циклу в Python
        cursor = await self.reviews.aggregate([
            {"$match": {"book_id": book_id}},
            {"$group": {"_id": None, "avg": {"$avg": "$rating"}, "count": {"$sum": 1}}},
        ])
        stats = await cursor.to_list()
        avg = round(stats[0]["avg"], 2) if stats else None
        return {"book_id": book_id, "avg_rating": avg, "count": len(reviews), "reviews": reviews}


ReviewServiceDep = Annotated[ReviewService, Depends()]
