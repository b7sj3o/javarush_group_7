from fastapi import FastAPI

from routers import auth, books, users, orders

app = FastAPI()

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(books.router)
app.include_router(orders.router)