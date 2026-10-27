from fastapi import APIRouter, Query

from schemas import GenreStats, TopRated
from services.books import BookServiceDep

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/genres", response_model=list[GenreStats])
async def genre_stats(service: BookServiceDep):
    return await service.genre_stats()


@router.get("/top-rated", response_model=list[TopRated])
async def top_rated(
    service: BookServiceDep,
    min_reviews: int = Query(default=1, ge=1),
    limit: int = Query(default=5, ge=1, le=20),
):
    return await service.top_rated(min_reviews, limit)
