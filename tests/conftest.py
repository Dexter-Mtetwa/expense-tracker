import os

import pytest
import psycopg
from fastapi.testclient import TestClient

from app.config import settings
from app.db.database import get_db
from app.main import app



TEST_DATABASE_URL = settings.test_database_url


# Automatically clean the database before each test
@pytest.fixture(autouse=True)
def clean_database():
    with psycopg.connect(TEST_DATABASE_URL) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                TRUNCATE TABLE expenses, categories, users
                RESTART IDENTITY CASCADE;
                """
            )
        connection.commit()


# Override the get_db dependency to use the test database
@pytest.fixture
def client():
    def override_get_db():
        connection = psycopg.connect(TEST_DATABASE_URL)

        try:
            yield connection
        finally:
            connection.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Provide a fixture for authenticated requests
@pytest.fixture
def auth_headers(client):
    email = "test@example.com"
    password = "testpassword123"

    response = client.post(
        "/api/v1/users",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 201

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


# Provide a fixture for a second authenticated user
@pytest.fixture
def second_user_headers(client):
    client.post(
        "/api/v1/users",
        json={
            "email": "second-user@example.com",
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "second-user@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    return {
        "Authorization": f"Bearer {token}",
    }


# Provide a fixture for creating a category
@pytest.fixture
def category(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Test Category"},
    )

    assert response.status_code == 201

    return response.json()


# Provide a fixture for creating an expense
@pytest.fixture
def expense(client, auth_headers, category):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Test Expense",
            "amount": 100,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201

    return response.json()