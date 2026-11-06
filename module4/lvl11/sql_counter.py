"""Скільки SQL-запитів зробив ендпоінт: заголовок X-SQL-Queries у кожній відповіді (видно в Swagger)."""

from contextvars import ContextVar

from fastapi import FastAPI, Request
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

_counter: ContextVar[dict[str, int] | None] = ContextVar("sql_counter", default=None)


def install_sql_counter(app: FastAPI, engine: AsyncEngine) -> None:
    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def count_query(conn, cursor, statement, parameters, context, executemany):
        box = _counter.get()
        if box is not None:
            box["n"] += 1

    @app.middleware("http")
    async def sql_queries_header(request: Request, call_next):
        # Лічильник у словнику, а не в int: ендпоінт працює в копії контексту, і зміну int ми б не побачили
        box = {"n": 0}
        _counter.set(box)
        response = await call_next(request)
        response.headers["X-SQL-Queries"] = str(box["n"])
        return response
