# Test the login endpoint
def test_login_returns_access_token(client):
    client.post(
        "/api/v1/users",
        json={
            "email": "login-test@example.com",
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "login-test@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# Test login with wrong password
def test_login_with_wrong_password(client):
    client.post(
        "/api/v1/users",
        json={
            "email": "wrong-password@example.com",
            "password": "testpassword123",
        },
    )

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "wrong-password@example.com",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email or password is incorrect"


# Test login with a non-existent user
def test_login_with_nonexistent_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "does-not-exist@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email or password is incorrect"


# Test that a protected endpoint requires authentication
def test_protected_endpoint_requires_authentication(client):
    response = client.get("/api/v1/expenses")

    assert response.status_code == 401


# Test that an invalid token is rejected
def test_invalid_token_is_rejected(client):
    response = client.get(
        "/api/v1/expenses",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


# Test that a regular user cannot access an admin-only endpoint
def test_admin_endpoint_rejects_regular_user(client, auth_headers):
    response = client.get(
        "/api/v1/users",
        headers=auth_headers,
    )

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient permissions"


# Test that an admin user can access an admin-only endpoint
def test_admin_endpoint_allows_admin_user(client):
    client.post(
        "/api/v1/users",
        json={
            "email": "admin-test@example.com",
            "password": "testpassword123",
        },
    )

    # Promote the test user directly in the test database.
    import psycopg
    from app.config import settings

    test_database_url = settings.test_database_url

    with psycopg.connect(test_database_url) as connection:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE users
                SET role = 'ADMIN'
                WHERE email = %s;
                """,
                ("admin-test@example.com",),
            )
        connection.commit()

    response = client.post(
        "/api/v1/auth/login",
        json={
            "email": "admin-test@example.com",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 200

    token = response.json()["access_token"]

    response = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)