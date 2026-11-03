from typing import Annotated

from fastapi import APIRouter, Path, status

from dependencies import CurrentUser
from schemas import BookReviews, ReviewCreate, ReviewOut
from services.reviews import ReviewServiceDep

router = APIRouter(prefix="/books/{book_id}/reviews", tags=["reviews"])

BookId = Annotated[int, Path(ge=1, description="Номер книги (id з Postgres)")]


@router.get("", response_model=BookReviews)
async def list_reviews(book_id: BookId, service: ReviewServiceDep):
    return await service.list(book_id)


@router.post("", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def add_review(book_id: BookId, data: ReviewCreate, user: CurrentUser, service: ReviewServiceDep):
    return await service.add(book_id, user, data)
