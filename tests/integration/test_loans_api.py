import pytest


@pytest.fixture
async def user(client):
    response = await client.post(
        "/users",
        json={"name": "Loan Test User", "email": "loan.user@email.com"},
    )
    return response.json()


@pytest.fixture
async def book(client):
    response = await client.post(
        "/books",
        json={"title": "Loan Test Book", "author": "Test Author"},
    )
    return response.json()


@pytest.fixture
async def books(client):
    result = []
    for i in range(4):
        response = await client.post(
            "/books",
            json={"title": f"Loan Book {i}", "author": "Test Author"},
        )
        result.append(response.json())
    return result


class TestCreateLoan:
    async def test_create_loan_success(self, client, user, book):
        response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["user_id"] == user["id"]
        assert data["book_id"] == book["id"]
        assert data["returned_at"] is None
        assert data["fine_cents"] == 0
        assert "due_to" in data

    async def test_create_loan_user_not_found(self, client, book):
        response = await client.post(
            "/loans",
            json={"user_id": 99999, "book_id": book["id"]},
        )

        assert response.status_code == 404
        assert response.json()["code"] == "user_not_found"

    async def test_create_loan_book_not_found(self, client, user):
        response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": 99999},
        )

        assert response.status_code == 404
        assert response.json()["code"] == "book_not_found"

    async def test_create_loan_book_already_loaned(self, client, user, book):
        await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )

        response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )

        assert response.status_code == 409
        assert response.json()["code"] == "book_already_loaned"

    async def test_create_loan_max_exceeded(self, client, user, books):
        # Create 3 loans (max allowed)
        for i in range(3):
            response = await client.post(
                "/loans",
                json={"user_id": user["id"], "book_id": books[i]["id"]},
            )
            assert response.status_code == 201

        # Try to create 4th loan
        response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": books[3]["id"]},
        )

        assert response.status_code == 409
        assert response.json()["code"] == "max_active_loans_exceeded"
        assert response.json()["context"]["active"] == 3


class TestReturnLoan:
    async def test_return_loan_success(self, client, user, book):
        loan_response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )
        loan_id = loan_response.json()["id"]

        response = await client.post(f"/loans/{loan_id}/return")

        assert response.status_code == 200
        assert response.json()["returned_at"] is not None

    async def test_return_loan_not_found(self, client):
        response = await client.post("/loans/99999/return")

        assert response.status_code == 404
        assert response.json()["code"] == "loan_not_found"

    async def test_return_loan_already_returned(self, client, user, book):
        loan_response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )
        loan_id = loan_response.json()["id"]

        await client.post(f"/loans/{loan_id}/return")
        response = await client.post(f"/loans/{loan_id}/return")

        assert response.status_code == 409
        assert response.json()["code"] == "loan_already_returned"

    async def test_can_loan_again_after_return(self, client, user, book):
        # Create and return loan
        loan_response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )
        loan_id = loan_response.json()["id"]
        await client.post(f"/loans/{loan_id}/return")

        # Loan same book again
        response = await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )

        assert response.status_code == 201


class TestListLoans:
    async def test_list_active_loans(self, client, user, book):
        await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )

        response = await client.get("/loans/active")

        assert response.status_code == 200
        assert len(response.json()) >= 1

    async def test_list_overdue_loans(self, client):
        response = await client.get("/loans/overdue")

        assert response.status_code == 200
        assert isinstance(response.json(), list)

    async def test_list_user_loans(self, client, user, book):
        await client.post(
            "/loans",
            json={"user_id": user["id"], "book_id": book["id"]},
        )

        response = await client.get(f"/users/{user['id']}/loans")

        assert response.status_code == 200
        assert len(response.json()) >= 1
