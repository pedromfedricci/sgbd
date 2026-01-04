class TestCreateBook:
    async def test_create_book_success(self, client):
        response = await client.post(
            "/books",
            json={"title": "Dom Casmurro", "author": "Machado de Assis"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Dom Casmurro"
        assert data["author"] == "Machado de Assis"
        assert "id" in data

    async def test_create_book_missing_title(self, client):
        response = await client.post(
            "/books",
            json={"author": "Machado de Assis"},
        )

        assert response.status_code == 422

    async def test_create_book_missing_author(self, client):
        response = await client.post(
            "/books",
            json={"title": "Dom Casmurro"},
        )

        assert response.status_code == 422


class TestGetBook:
    async def test_get_book_success(self, client):
        create_response = await client.post(
            "/books",
            json={"title": "Test Book", "author": "Test Author"},
        )
        book_id = create_response.json()["id"]

        response = await client.get(f"/books/{book_id}")

        assert response.status_code == 200
        assert response.json()["id"] == book_id
        assert response.json()["title"] == "Test Book"

    async def test_get_book_not_found(self, client):
        response = await client.get("/books/99999")

        assert response.status_code == 404
        assert response.json()["code"] == "book_not_found"


class TestListBooks:
    async def test_list_books(self, client):
        await client.post("/books", json={"title": "Book 1", "author": "Author 1"})
        await client.post("/books", json={"title": "Book 2", "author": "Author 2"})

        response = await client.get("/books")

        assert response.status_code == 200
        assert len(response.json()) >= 2

    async def test_list_books_pagination(self, client):
        for i in range(5):
            await client.post(
                "/books", json={"title": f"Page Book {i}", "author": f"Author {i}"}
            )

        response = await client.get("/books?offset=0&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2
