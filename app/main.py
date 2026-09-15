from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException
from psycopg import Connection
import psycopg

from app.db.database import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse, Token
from app.schemas.expenses import ExpenseCreate, ExpenseResponse
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


@app.get('/db-test')
def db_test(connection: Connection = Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()

    return {'db_test_result': result[0]}