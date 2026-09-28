# ---test category CRUD---

# Test the create endpoint for categories
def test_create_category(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Food"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Food"
    assert "id" in data
    assert "created_at" in data


# Test the list endpoint for categories
def test_list_categories(client, auth_headers, category):
    response = client.get(
        "/api/v1/categories",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == category["id"]
    assert data[0]["name"] == "Test Category"


# Test the get endpoint for a specific category
def test_get_category(client, auth_headers, category):
    response = client.get(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == category["id"]
    assert data["name"] == "Test Category"


# Test the update endpoint for a specific category
def test_update_category(client, auth_headers, category):
    response = client.patch(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
        json={"name": "Updated Category"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == category["id"]
    assert data["name"] == "Updated Category"


# Test the delete endpoint for a specific category
def test_delete_category(client, auth_headers, category):
    response = client.delete(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 404




# ---test category error/validation cases---

# Test creating a category with a duplicate name
def test_create_duplicate_category(client, auth_headers):
    client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Food"},
    )

    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "Food"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Category already exists"


# Test creating a category with a blank name
def test_create_blank_category(client, auth_headers):
    response = client.post(
        "/api/v1/categories",
        headers=auth_headers,
        json={"name": "   "},
    )

    assert response.status_code == 422


# Test updating a category with no fields provided
def test_update_category_with_no_fields(client, auth_headers, category):
    response = client.patch(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields provided for update"


# Test updating a non-existent category
def test_get_nonexistent_category(client, auth_headers):
    response = client.get(
        "/api/v1/categories/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# Test updating a non-existent category
def test_update_nonexistent_category(client, auth_headers):
    response = client.patch(
        "/api/v1/categories/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
        json={"name": "Updated"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


# Test deleting a non-existent category
def test_delete_nonexistent_category(client, auth_headers):
    response = client.delete(
        "/api/v1/categories/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"




# ---test category in use cases---

# Test updating a category that is in use
def test_update_category_in_use(client, auth_headers, category, expense):
    response = client.patch(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
        json={"name": "Updated Category"},
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Category is in use"


# Test deleting a category that is in use
def test_delete_category_in_use(client, auth_headers, category, expense):
    response = client.delete(
        f"/api/v1/categories/{category['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Category is in use"