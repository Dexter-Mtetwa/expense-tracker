from fastapi import Depends, FastAPI, HTTPException
from psycopg import Connection
import psycopg

from app.db.database import get_db
from app.schemas.users import UserCreate, UserLogin, UserResponse
from app.security import hash_password, verify_password

app = FastAPI()


@app.get('/')
def root():
    return {'message': 'Expense Tracker API'}


@app.get('/health')
def health_check():
    return {'status': 'ok'}


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


@app.post('/login')
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
        raise HTTPException(status_code=401, detail="wakapusa")

    return {
        'id': str(existing_user[0]),
        'email': existing_user[1],
        'role': existing_user[3],
        'created_at': existing_user[4].isoformat()
    }



@app.get('/db-test')
def db_test(connection: Connection = Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()

    return {'db_test_result': result[0]}