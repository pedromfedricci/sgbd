class TestCreateUser:
    async def test_create_user_success(self, client):
        response = await client.post(
            "/users",
            json={"name": "Test User", "email": "test@email.com"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test User"
        assert data["email"] == "test@email.com"
        assert "id" in data

    async def test_create_user_duplicate_email(self, client):
        await client.post(
            "/users",
            json={"name": "First User", "email": "duplicate@email.com"},
        )

        response = await client.post(
            "/users",
            json={"name": "Second User", "email": "duplicate@email.com"},
        )

        assert response.status_code == 409
        assert response.json()["code"] == "email_already_registered"

    async def test_create_user_invalid_email(self, client):
        response = await client.post(
            "/users",
            json={"name": "Test", "email": "invalid-email"},
        )

        assert response.status_code == 422

    async def test_create_user_missing_fields(self, client):
        response = await client.post("/users", json={})

        assert response.status_code == 422


class TestGetUser:
    async def test_get_user_success(self, client):
        create_response = await client.post(
            "/users",
            json={"name": "Get Test", "email": "get.test@email.com"},
        )
        user_id = create_response.json()["id"]

        response = await client.get(f"/users/{user_id}")

        assert response.status_code == 200
        assert response.json()["id"] == user_id
        assert response.json()["name"] == "Get Test"

    async def test_get_user_not_found(self, client):
        response = await client.get("/users/99999")

        assert response.status_code == 404
        assert response.json()["code"] == "user_not_found"


class TestListUsers:
    async def test_list_users(self, client):
        await client.post("/users", json={"name": "User 1", "email": "user1@email.com"})
        await client.post("/users", json={"name": "User 2", "email": "user2@email.com"})

        response = await client.get("/users")

        assert response.status_code == 200
        assert len(response.json()) >= 2

    async def test_list_users_pagination(self, client):
        for i in range(5):
            await client.post(
                "/users", json={"name": f"Page User {i}", "email": f"page{i}@email.com"}
            )

        response = await client.get("/users?offset=0&limit=2")

        assert response.status_code == 200
        assert len(response.json()) == 2


class TestGetUserLoans:
    async def test_get_user_loans_empty(self, client):
        create_response = await client.post(
            "/users",
            json={"name": "Loans Test", "email": "loans.test@email.com"},
        )
        user_id = create_response.json()["id"]

        response = await client.get(f"/users/{user_id}/loans")

        assert response.status_code == 200
        assert response.json() == []

    async def test_get_user_loans_not_found(self, client):
        response = await client.get("/users/99999/loans")

        assert response.status_code == 404
