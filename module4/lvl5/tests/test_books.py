import pytest


def test_list_books_success(client):
    response = client.get("/books")
    
    assert response.status_code == 200
    assert len(response.json()) == 6
    
    
def test_list_books_filter_by_genre_success(client):
    response = client.get("/books?genre=novel")
    
    assert response.status_code == 200
    assert len(response.json()) == 3
    assert all(book["genre"] == "novel" for book in response.json())
    
    
def test_list_books_filter_by_genre_error(client):
    response = client.get("/books?genre=sawawsaws")
    
    assert response.status_code == 422

def test_list_books_pagination_success(client):
    response = client.get("/books?offset=2&limit=2")
    
    assert response.status_code == 200
    
    data = response.json()
    
    assert len(data) == 2
    assert data[0]["id"] == 3
    assert data[1]["id"] == 4
    
    
def test_get_book_success(client):
    response = client.get("/books/1")
    assert response.status_code == 200
    assert response.json()["title"] == "Кобзар"
    assert response.json()["author"]["name"] == "Тарас Шевченко"


def test_get_book_not_found(client):
    response = client.get("/books/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Книгу з id=999 не знайдено"}
    
    
import pytest


@pytest.mark.parametrize(
    "params",
    [
        {"limit": 100},
        {"genre": "comics"},
        {"year_from": 1950, "year_to": 1900},
        {"page": 2},  # extra="forbid": невідомий параметр теж помилка
    ],
)
def test_list_books_bad_filters(client, params):
    assert client.get("/books", params=params).status_code == 422


@pytest.mark.parametrize("book_id", ["0", "-1", "abc"])
def test_get_book_bad_id(client, book_id):
    assert client.get(f"/books/{book_id}").status_code == 422