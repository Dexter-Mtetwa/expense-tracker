# Test creating an expense
def test_create_expense(client, auth_headers, category):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Groceries",
            "description": "Weekly groceries",
            "amount": 50.75,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["name"] == "Groceries"
    assert data["description"] == "Weekly groceries"
    assert data["amount"] == "50.75"
    assert data["category_id"] == category["id"]
    assert "id" in data
    assert "created_at" in data


# Test listing expenses
def test_list_expenses(client, auth_headers, category, expense):
    response = client.get(
        "/api/v1/expenses",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == expense["id"]


# Test retrieving a single expense
def test_get_expense(client, auth_headers, expense):
    response = client.get(
        f"/api/v1/expenses/{expense['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense["id"]
    assert data["name"] == "Test Expense"


# Test updating an expense
def test_update_expense(client, auth_headers, expense):
    response = client.patch(
        f"/api/v1/expenses/{expense['id']}",
        headers=auth_headers,
        json={
            "name": "Updated Expense",
            "amount": 150,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == expense["id"]
    assert data["name"] == "Updated Expense"
    assert data["amount"] == "150.00"


# Test deleting an expense
def test_delete_expense(client, auth_headers, expense):
    response = client.delete(
        f"/api/v1/expenses/{expense['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 204

    response = client.get(
        f"/api/v1/expenses/{expense['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 404


# Test filtering expenses by category
def test_filter_expenses_by_category(client, auth_headers, category):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Category Expense",
            "amount": 75,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201

    response = client.get(
        f"/api/v1/expenses?category_id={category['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["category_id"] == category["id"]
    assert data[0]["name"] == "Category Expense"


# Test total spent across all expenses
def test_total_spent(client, auth_headers, category):
    for amount in (25, 50.50):
        response = client.post(
            "/api/v1/expenses",
            headers=auth_headers,
            json={
                "name": f"Expense {amount}",
                "amount": amount,
                "date": "2026-09-28",
                "category_id": category["id"],
            },
        )

        assert response.status_code == 201

    response = client.get(
        "/api/v1/expenses/total",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 75.50


# Test total spent by category
def test_total_spent_by_category(client, auth_headers, category):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Category Expense",
            "amount": 75,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201

    response = client.get(
        f"/api/v1/expenses/total?category_id={category['id']}",
        headers=auth_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 75.00



# ---test expense error/validation cases---

# Test creating an expense with a non-existent category
def test_create_expense_with_nonexistent_category(client, auth_headers):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Invalid Category Expense",
            "amount": 25,
            "date": "2026-09-28",
            "category_id": "00000000-0000-0000-0000-000000000000",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Category does not exist"


# Test creating an expense with a negative amount
def test_create_expense_with_negative_amount(client, auth_headers, category):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Invalid Amount",
            "amount": -10,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 422


# Test creating an expense with a blank name
def test_create_expense_with_blank_name(client, auth_headers, category):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "   ",
            "amount": 10,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 422


# Test updating an expense with no fields provided
def test_update_expense_with_no_fields(client, auth_headers, expense):
    response = client.patch(
        f"/api/v1/expenses/{expense['id']}",
        headers=auth_headers,
        json={},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "No fields provided for update"


# Test getting a non-existent expense
def test_get_nonexistent_expense(client, auth_headers):
    response = client.get(
        "/api/v1/expenses/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


# Test updating a non-existent expense
def test_update_nonexistent_expense(client, auth_headers):
    response = client.patch(
        "/api/v1/expenses/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
        json={"name": "Updated"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"


# Test deleting a non-existent expense
def test_delete_nonexistent_expense(client, auth_headers):
    response = client.delete(
        "/api/v1/expenses/00000000-0000-0000-0000-000000000000",
        headers=auth_headers,
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Expense not found"




# Test that a user cannot access another user's expense
def test_user_cannot_get_another_users_expense(
    client,
    auth_headers,
    category,
    second_user_headers,
):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Private Expense",
            "amount": 100,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = client.get(
        f"/api/v1/expenses/{expense_id}",
        headers=second_user_headers,
    )

    assert response.status_code == 404


# Test that a user cannot update another user's expense
def test_user_cannot_update_another_users_expense(
    client,
    auth_headers,
    category,
    second_user_headers,
):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Private Expense",
            "amount": 100,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = client.patch(
        f"/api/v1/expenses/{expense_id}",
        headers=second_user_headers,
        json={"name": "Hijacked Expense"},
    )

    assert response.status_code == 404


# Test that a user cannot delete another user's expense
def test_user_cannot_delete_another_users_expense(
    client,
    auth_headers,
    category,
    second_user_headers,
):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "Private Expense",
            "amount": 100,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201
    expense_id = response.json()["id"]

    response = client.delete(
        f"/api/v1/expenses/{expense_id}",
        headers=second_user_headers,
    )

    assert response.status_code == 404

    # Confirm the original owner still has the expense.
    response = client.get(
        f"/api/v1/expenses/{expense_id}",
        headers=auth_headers,
    )

    assert response.status_code == 200


# Test that a user cannot see another user's expenses
def test_user_cannot_see_another_users_expenses(
    client,
    auth_headers,
    category,
    second_user_headers,
):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "First User Expense",
            "amount": 100,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201

    response = client.get(
        "/api/v1/expenses",
        headers=second_user_headers,
    )

    assert response.status_code == 200
    assert response.json() == []


# Test that a user cannot see another user's total
def test_user_cannot_see_another_users_total(
    client,
    auth_headers,
    category,
    second_user_headers,
):
    response = client.post(
        "/api/v1/expenses",
        headers=auth_headers,
        json={
            "name": "First User Expense",
            "amount": 100,
            "date": "2026-09-28",
            "category_id": category["id"],
        },
    )

    assert response.status_code == 201

    response = client.get(
        "/api/v1/expenses/total",
        headers=second_user_headers,
    )

    assert response.status_code == 200
    assert response.json()["total"] == 0

