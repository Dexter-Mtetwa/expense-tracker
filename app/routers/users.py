from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection
import psycopg

from app.db.database import get_db
from app.schemas.users import Token, UserCreate, UserLogin, UserResponse
from app.security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/users", tags=["Users"])


# create user
@router.post('', response_model=UserResponse, status_code=201)
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


