"""seed data

Revision ID: e3c791e8f290
Revises: 62a6a1076bd8
Create Date: 2026-10-30 18:07:06.923467

"""
from datetime import date
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3c791e8f290'
down_revision: Union[str, Sequence[str], None] = '62a6a1076bd8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Таблиці описані тут, а не імпортовані з models.py: моделі з часом зміняться,
# а міграція має назавжди лишитися такою, якою була в день написання.
users = sa.table(
    "users",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("email", sa.String),
    sa.column("hashed_password", sa.String),
    sa.column("role", sa.Enum("READER", "MANAGER", "ADMIN", name="role")),
    sa.column("is_active", sa.Boolean),
)
authors = sa.table(
    "authors",
    sa.column("id", sa.Integer),
    sa.column("name", sa.String),
    sa.column("born", sa.Integer),
)
books = sa.table(
    "books",
    sa.column("id", sa.Integer),
    sa.column("title", sa.String),
    sa.column("year", sa.Integer),
    sa.column("genre", sa.Enum("POETRY", "NOVEL", "DRAMA", "HISTORY", name="genre")),
    sa.column("isbn", sa.String),
    sa.column("available", sa.Boolean),
    sa.column("added_at", sa.Date),
)
authors_books = sa.table(
    "authors_books_table",
    sa.column("author_id", sa.Integer),
    sa.column("book_id", sa.Integer),
)

# Готові argon2-хеші паролів admin12345, manager12345, secret123.
# Хеш, а не hash_password(): міграція не залежить від коду застосунку.
ADMIN_HASH = "$argon2id$v=19$m=65536,t=3,p=4$yvyk7Id47AvpEFh8ytQwqA$Otqr0EE/yBPYAvb2idhdwhVzvW+C2vIiJ7K7t41syAg"
MANAGER_HASH = "$argon2id$v=19$m=65536,t=3,p=4$6444BS5BLwH5ItCelIDYkA$zocr226ohuW6PRje2W+go5H5izLyjydWFdo3DxWgth8"
READER_HASH = "$argon2id$v=19$m=65536,t=3,p=4$WyEzkd4ZIJnvCsF1EGP63g$+bKFJ+UQrYDrHN0v8PIAFEC/hJ/lkjL3zl24qAHxmu0"


def upgrade() -> None:
    op.bulk_insert(users, [
        {"id": 1, "name": "Адмін", "email": "admin@library.ua", "hashed_password": ADMIN_HASH,
         "role": "ADMIN", "is_active": True},
        {"id": 2, "name": "Менеджер", "email": "manager@library.ua", "hashed_password": MANAGER_HASH,
         "role": "MANAGER", "is_active": True},
        {"id": 3, "name": "Оля", "email": "olia@example.com", "hashed_password": READER_HASH,
         "role": "READER", "is_active": True},
        {"id": 4, "name": "Неактивний", "email": "off@example.com", "hashed_password": READER_HASH,
         "role": "READER", "is_active": False},
    ])
    op.bulk_insert(authors, [
        {"id": 1, "name": "Тарас Шевченко", "born": 1814},
        {"id": 2, "name": "Іван Франко", "born": 1856},
        {"id": 3, "name": "Леся Українка", "born": 1871},
        {"id": 4, "name": "Валер'ян Підмогильний", "born": 1901},
        {"id": 5, "name": "Іван Багряний", "born": 1906},
    ])
    op.bulk_insert(books, [
        {"id": 1, "title": "Кобзар", "year": 1840, "genre": "POETRY", "isbn": "9789660301016",
         "available": True, "added_at": date(2026, 10, 1)},
        {"id": 2, "title": "Захар Беркут", "year": 1883, "genre": "HISTORY", "isbn": None,
         "available": True, "added_at": date(2026, 10, 1)},
        {"id": 3, "title": "Лісова пісня", "year": 1911, "genre": "DRAMA", "isbn": None,
         "available": True, "added_at": date(2026, 10, 1)},
        {"id": 4, "title": "Місто", "year": 1928, "genre": "NOVEL", "isbn": None,
         "available": True, "added_at": date(2026, 10, 2)},
        {"id": 5, "title": "Тигролови", "year": 1944, "genre": "NOVEL", "isbn": None,
         "available": False, "added_at": date(2026, 10, 2)},
        {"id": 6, "title": "Сад Гетсиманський", "year": 1950, "genre": "NOVEL", "isbn": "9789660312227",
         "available": True, "added_at": date(2026, 10, 3)},
    ])
    op.bulk_insert(authors_books, [
        {"author_id": 1, "book_id": 1},
        {"author_id": 2, "book_id": 2},
        {"author_id": 3, "book_id": 3},
        {"author_id": 4, "book_id": 4},
        {"author_id": 5, "book_id": 5},
        {"author_id": 5, "book_id": 6},
    ])
    # id ми вписали руками, тож лічильники (sequence) досі на 1.
    # Без setval перший же POST /books впаде з duplicate key value violates unique constraint "books_pkey".
    for table in ("users", "authors", "books"):
        op.execute(f"SELECT setval('{table}_id_seq', (SELECT max(id) FROM {table}))")


def downgrade() -> None:
    op.execute("DELETE FROM authors_books_table WHERE book_id <= 6")
    op.execute("DELETE FROM books WHERE id <= 6")
    op.execute("DELETE FROM authors WHERE id <= 5")
    op.execute("DELETE FROM users WHERE id <= 4")
