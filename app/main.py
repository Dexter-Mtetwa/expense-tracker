from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException
from psycopg import Connection
import psycopg

from app.db.database import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse, Token
from app.schemas.expenses import ExpenseCreate, ExpenseResponse, ExpenseUpdate
from app.schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate
from app.security import (hash_password, verify_password, create_access_token)
from app.dependencies import get_current_user


app = FastAPI()


@app.get('/')
def root():
    return {'message': 'Expense Tracker API'}


@app.get('/health')
def health_check():
    return {'status': 'ok'}


# ---user oriented endpoints---
@app.post('/users', response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, connection: Connection = Depends(get_db)):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (email, password_hash)
                VALUES (%s, %s)
                RETURNING id, email, role, created_at;
                """,
                (user.email, hash_password(user.password))
            )
            user = cursor.fetchone()

        connection.commit()

        return {
            'id': str(user[0]),
            'email': user[1],
            'role': user[2],
            'created_at': user[3].isoformat()
        }
    except psycopg.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")


@app.post('/login', response_model=Token)
def login(user: UserLogin, connection: Connection = Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, password_hash, role, created_at
            FROM users
            WHERE email = %s;
            """,
            (user.email,)
        )
        existing_user = cursor.fetchone()

    if not existing_user or not verify_password(user.password, existing_user[2]):
        raise HTTPException(status_code=401, detail="Email or password is incorrect")

    access_token = create_access_token(
        data={'sub': str(existing_user[0])},
        expires_delta=timedelta(minutes=30)
    )

    return {
        'access_token': access_token,
        'token_type': 'bearer'
    }




# ---expense oriented endpoints---
@app.post("/expenses", response_model=ExpenseResponse, status_code=201)
def create_expense(
    expense: ExpenseCreate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO expenses (
                    name,
                    description,
                    amount,
                    date,
                    user_id,
                    category_id
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id, name, description, amount, date, created_at, category_id;
                """,
                (
                    expense.name,
                    expense.description,
                    expense.amount,
                    expense.date,
                    user_id,
                    expense.category_id,
                ),
            )

            created_expense = cursor.fetchone()

        connection.commit()

    except psycopg.errors.ForeignKeyViolation:
        connection.rollback()

        raise HTTPException(
            status_code=404,
            detail="Category does not exist",
        )

    return {
        "id": str(created_expense[0]),
        "name": created_expense[1],
        "description": created_expense[2],
        "amount": created_expense[3],
        "date": created_expense[4],
        "created_at": created_expense[5],
        "category_id": str(created_expense[6]),
    }


# Get all expenses for the current user
@app.get("/expenses", response_model=list[ExpenseResponse])
def get_expenses(
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description, amount, date, created_at, category_id
            FROM expenses
            WHERE user_id = %s
            ORDER BY date DESC, created_at DESC;
            """,
            (user_id,),
        )

        expenses = cursor.fetchall()

    return [
        {
            "id": str(expense[0]),
            "name": expense[1],
            "description": expense[2],
            "amount": expense[3],
            "date": expense[4],
            "created_at": expense[5],
            "category_id": str(expense[6]),
        }
        for expense in expenses
    ]


# Get a specific expense by ID for the current user
@app.get("/expenses/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description, amount, date, created_at, category_id
            FROM expenses
            WHERE id = %s
            AND user_id = %s;
            """,
            (expense_id, user_id),
        )

        expense = cursor.fetchone()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    return {
        "id": str(expense[0]),
        "name": expense[1],
        "description": expense[2],
        "amount": expense[3],
        "date": expense[4],
        "created_at": expense[5],
        "category_id": str(expense[6]),
    }


# Update a specific expense by ID for the current user
@app.patch("/expenses/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: str,
    expense: ExpenseUpdate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    updates = expense.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    set_clauses = []
    values = []

    for field, value in updates.items():
        set_clauses.append(f"{field} = %s")
        values.append(value)

    values.extend([expense_id, user_id])

    query = f"""
        UPDATE expenses
        SET {", ".join(set_clauses)}
        WHERE id = %s
        AND user_id = %s
        RETURNING id, name, description, amount, date, created_at, category_id;
    """

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            updated_expense = cursor.fetchone()

        if not updated_expense:
            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        connection.commit()

    except psycopg.errors.ForeignKeyViolation:
        connection.rollback()

        raise HTTPException(
            status_code=404,
            detail="Category does not exist",
        )

    return {
        "id": str(updated_expense[0]),
        "name": updated_expense[1],
        "description": updated_expense[2],
        "amount": updated_expense[3],
        "date": updated_expense[4],
        "created_at": updated_expense[5],
        "category_id": str(updated_expense[6]),
    }


# Delete a specific expense by ID for the current user
@app.delete("/expenses/{expense_id}", status_code=204)
def delete_expense(
    expense_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM expenses
                WHERE id = %s
                AND user_id = %s
                RETURNING id;
                """,
                (expense_id, user_id),
            )

            deleted_expense = cursor.fetchone()

        if not deleted_expense:
            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        connection.commit()

    except psycopg.Error:
        connection.rollback()
        raise



# ---category oriented endpoints---
@app.post("/categories", response_model=CategoryResponse, status_code=201)
def create_category(
    category: CategoryCreate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO categories (name, creator)
                VALUES (%s, %s)
                RETURNING id, name, created_at;
                """,
                (category.name, user_id),
            )

            created_category = cursor.fetchone()

        connection.commit()

    except psycopg.errors.UniqueViolation:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail="Category already exists",
        )

    return {
        "id": str(created_category[0]),
        "name": created_category[1],
        "created_at": created_category[2],
    }


# Get all categories
@app.get("/categories", response_model=list[CategoryResponse])
def get_categories(
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, created_at
            FROM categories
            ORDER BY name;
            """
        )

        categories = cursor.fetchall()

    return [
        {
            "id": str(category[0]),
            "name": category[1],
            "created_at": category[2],
        }
        for category in categories
    ]


# Get a specific category by ID
@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, created_at
            FROM categories
            WHERE id = %s;
            """,
            (category_id,),
        )

        category = cursor.fetchone()

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return {
        "id": str(category[0]),
        "name": category[1],
        "created_at": category[2],
    }


# Update a specific category by ID
@app.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: str,
    category: CategoryUpdate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    updates = category.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    # Check if the category is in use before updating the name
    if "name" in updates:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM expenses
                WHERE category_id = %s
                LIMIT 1;
                """,
                (category_id,),
            )

            category_in_use = cursor.fetchone()

        if category_in_use:
            raise HTTPException(
                status_code=409,
                detail="Category is in use",
            )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE categories
                SET name = %s
                WHERE id = %s
                AND creator = %s
                RETURNING id, name, created_at;
                """,
                (
                    updates["name"],
                    category_id,
                    user_id,
                ),
            )

            updated_category = cursor.fetchone()

        if not updated_category:
            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        connection.commit()

    except psycopg.errors.UniqueViolation:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail="Category already exists",
        )

    return {
        "id": str(updated_category[0]),
        "name": updated_category[1],
        "created_at": updated_category[2],
    }


# Delete a specific category by ID
@app.delete("/categories/{category_id}", status_code=204)
def delete_category(
    category_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM categories
                WHERE id = %s
                AND creator = %s
                RETURNING id;
                """,
                (category_id, user_id),
            )

            deleted_category = cursor.fetchone()

        if not deleted_category:
            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        connection.commit()

    except psycopg.errors.ForeignKeyViolation:
        connection.rollback()

        raise HTTPException(
            status_code=409,
            detail="Category is in use",
        )

    
@app.get('/db-test')
def db_test(connection: Connection = Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()

    return {'db_test_result': result[0]}