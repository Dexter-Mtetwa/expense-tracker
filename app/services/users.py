import psycopg
from fastapi import HTTPException
from psycopg import Connection

from app.repositories import users as user_repository
from app.security import hash_password


def create_user(user, connection: Connection):
    password_hash = hash_password(user.password)

    try:
        created_user = user_repository.create_user(
            connection=connection,
            email=user.email,
            password_hash=password_hash,
        )
        connection.commit()
    except psycopg.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(status_code=409, detail="Email already exists")

    return {
        "id": str(created_user[0]),
        "email": created_user[1],
        "role": created_user[2],
        "created_at": created_user[3].isoformat(),
    }


def get_users(connection: Connection):
    users = user_repository.get_users(connection=connection)

    return [
        {
            "id": str(user[0]),
            "email": user[1],
            "role": user[2],
            "created_at": user[3],
        }
        for user in users
    ]