"""Колекція books: правило перевірки ($jsonSchema), індекси і стартові дані."""

from datetime import UTC, datetime

from pymongo.asynchronous.database import AsyncDatabase

BOOK_VALIDATOR = {
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["title", "authors", "year", "genre", "edition"],
        "properties": {
            "title": {"bsonType": "string", "minLength": 1},
            "authors": {
                "bsonType": "array",
                "minItems": 1,
                "items": {"bsonType": "object", "required": ["name"]},
            },
            "year": {"bsonType": "int", "minimum": 1450, "maximum": 2100},
            "genre": {"enum": ["poetry", "novel", "drama", "history"]},
            "edition": {
                "bsonType": "object",
                "required": ["format"],
                "properties": {"format": {"enum": ["paper", "ebook", "audio"]}},
            },
            "reviews": {
                "bsonType": "array",
                "items": {
                    "bsonType": "object",
                    "required": ["user", "rating"],
                    "properties": {"rating": {"bsonType": "int", "minimum": 1, "maximum": 5}},
                },
            },
        },
    }
}


def _review(user: str, rating: int, text: str) -> dict:
    return {"user": user, "rating": rating, "text": text, "created_at": datetime(2026, 10, 20, tzinfo=UTC)}


def _seed_books() -> list[dict]:
    added = datetime(2026, 10, 1, tzinfo=UTC)
    shevchenko = {"name": "Тарас Шевченко", "born": 1814}
    franko = {"name": "Іван Франко", "born": 1856}
    ukrainka = {"name": "Леся Українка", "born": 1871}
    pidmohylny = {"name": "Валер'ян Підмогильний", "born": 1901}
    bahrianyi = {"name": "Іван Багряний", "born": 1906}
    return [
        {
            "title": "Кобзар", "authors": [shevchenko], "year": 1840, "genre": "poetry",
            "edition": {"format": "paper", "pages": 704, "isbn": "9789660301016"},
            "tags": ["класика"], "added_at": added,
            "reviews": [_review("olia", 5, "Must read"), _review("petro", 4, "Гарне видання")],
        },
        {
            "title": "Захар Беркут", "authors": [franko], "year": 1883, "genre": "history",
            "edition": {"format": "ebook", "file_format": "epub", "size_mb": 1.2},
            "tags": [], "added_at": added, "reviews": [_review("olia", 4, "")],
        },
        {
            "title": "Лісова пісня", "authors": [ukrainka], "year": 1911, "genre": "drama",
            "edition": {"format": "audio", "narrator": "Олена Голос", "duration_min": 185},
            "tags": ["класика", "п'єса"], "added_at": added, "reviews": [],
        },
        {
            "title": "Місто", "authors": [pidmohylny], "year": 1928, "genre": "novel",
            "edition": {"format": "paper", "pages": 368},
            "tags": [], "added_at": added,
            "reviews": [_review("petro", 5, "Київ 1920-х як живий"), _review("ira", 5, "")],
        },
        {
            "title": "Тигролови", "authors": [bahrianyi], "year": 1944, "genre": "novel",
            "edition": {"format": "ebook", "file_format": "pdf", "size_mb": 3.4},
            "tags": ["пригоди"], "added_at": added, "reviews": [_review("ira", 3, "Затягнуто на початку")],
        },
        {
            "title": "Сад Гетсиманський", "authors": [bahrianyi], "year": 1950, "genre": "novel",
            "edition": {"format": "paper", "pages": 512, "isbn": "9789660312227"},
            "tags": [], "added_at": added, "reviews": [],
        },
    ]


async def init_db(db: AsyncDatabase) -> None:
    """Правило перевірки, індекси і стартові дані. Безпечно викликати на кожному старті."""
    if "books" not in await db.list_collection_names():
        await db.create_collection("books", validator=BOOK_VALIDATOR)
    else:
        await db.command("collMod", "books", validator=BOOK_VALIDATOR)

    books = db["books"]
    await books.create_index("authors.name")
    await books.create_index([("genre", 1), ("year", -1)])

    if await books.count_documents({}) == 0:
        await books.insert_many(_seed_books())
