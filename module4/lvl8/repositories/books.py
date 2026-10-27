import re
from collections.abc import Sequence
from typing import Any

from bson import ObjectId
from pymongo import ReturnDocument
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.collation import Collation

from schemas import BookFilter

# strength=2: порівняння без урахування регістру, з українськими літерами теж («кобзар» == «Кобзар»)
CASE_INSENSITIVE = Collation(locale="uk", strength=2)


class BookRepository:
    """Лише запити до колекції books. Жодних HTTP-помилок."""

    def __init__(self, db: AsyncDatabase):
        self.books = db["books"]

    async def get(self, book_id: ObjectId) -> dict[str, Any] | None:
        return await self.books.find_one({"_id": book_id})

    async def list(self, filters: BookFilter) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if filters.author:
            # authors — масив документів; "authors.name" шукає по name кожного елемента
            query["authors.name"] = {"$regex": re.escape(filters.author), "$options": "i"}
        if filters.q:
            query["title"] = {"$regex": re.escape(filters.q), "$options": "i"}
        if filters.genre:
            query["genre"] = filters.genre
        if filters.format:
            query["edition.format"] = filters.format
        years: dict[str, int] = {}
        if filters.year_from is not None:
            years["$gte"] = filters.year_from
        if filters.year_to is not None:
            years["$lte"] = filters.year_to
        if years:
            query["year"] = years

        # projection {"reviews": 0}: відгуки в списку не потрібні, не тягнемо їх із бази
        cursor = (
            self.books.find(query, {"reviews": 0})
            .sort([(filters.sort, 1), ("_id", 1)])
            .skip(filters.offset)
            .limit(filters.limit)
        )
        return await cursor.to_list()

    async def find_duplicate(self, title: str, author_names: Sequence[str]) -> dict[str, Any] | None:
        """Книга з такою самою назвою, у якої є хоч один із цих авторів (без урахування регістру)."""
        # Sequence, а не list: усередині класу ім'я list уже зайняте методом list() вище
        query = {"title": title, "authors.name": {"$in": author_names}}
        return await self.books.find_one(query, collation=CASE_INSENSITIVE)

    async def insert(self, doc: dict[str, Any]) -> ObjectId:
        result = await self.books.insert_one(doc)
        return result.inserted_id

    async def update(self, book_id: ObjectId, fields: dict[str, Any]) -> dict[str, Any] | None:
        # $set міняє лише передані поля; AFTER повертає документ уже після зміни
        return await self.books.find_one_and_update(
            {"_id": book_id}, {"$set": fields}, return_document=ReturnDocument.AFTER
        )

    async def delete(self, book_id: ObjectId) -> bool:
        result = await self.books.delete_one({"_id": book_id})
        return result.deleted_count == 1

    async def add_review(self, book_id: ObjectId, review: dict[str, Any]) -> bool:
        # $push дописує відгук у масив усередині книги: окрема таблиця reviews не потрібна
        result = await self.books.update_one({"_id": book_id}, {"$push": {"reviews": review}})
        return result.matched_count == 1

    async def genre_stats(self) -> Sequence[dict[str, Any]]:
        # Аналог SELECT genre, count(*), min(year), max(year) FROM books GROUP BY genre ORDER BY 2 DESC
        pipeline = [
            {"$group": {
                "_id": "$genre",
                "books": {"$sum": 1},
                "first_year": {"$min": "$year"},
                "last_year": {"$max": "$year"},
            }},
            {"$sort": {"books": -1, "_id": 1}},
            {"$project": {"_id": 0, "genre": "$_id", "books": 1, "first_year": 1, "last_year": 1}},
        ]
        cursor = await self.books.aggregate(pipeline)
        return await cursor.to_list()

    async def top_rated(self, min_reviews: int, limit: int) -> Sequence[dict[str, Any]]:
        pipeline = [
            {"$unwind": "$reviews"},  # одна книга з 3 відгуками -> 3 документи, по відгуку в кожному
            {"$group": {
                "_id": "$_id",
                "title": {"$first": "$title"},
                "avg_rating": {"$avg": "$reviews.rating"},
                "reviews": {"$sum": 1},
            }},
            {"$match": {"reviews": {"$gte": min_reviews}}},  # $match після $group = HAVING
            {"$sort": {"avg_rating": -1, "reviews": -1, "_id": 1}},
            {"$limit": limit},
            {"$set": {"avg_rating": {"$round": ["$avg_rating", 2]}}},
        ]
        cursor = await self.books.aggregate(pipeline)
        return await cursor.to_list()
