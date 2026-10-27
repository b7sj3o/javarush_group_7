"""Помилки сервісного шару. Сервіс каже «не знайдено» чи «конфлікт», а не підбирає статус-коди сам."""

from typing import Any

from fastapi import HTTPException, status


class NotFoundError(HTTPException):
    def __init__(self, detail: str):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)


class ConflictError(HTTPException):
    def __init__(self, detail: Any):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)
