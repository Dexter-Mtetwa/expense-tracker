from fastapi import HTTPException
from psycopg import Connection
import psycopg

from app.security import hash_password

def create_user(
    user,
    connection: Connection
):
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