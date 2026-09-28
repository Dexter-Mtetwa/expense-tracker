from datetime import timedelta

from fastapi import HTTPException
from psycopg import Connection

from app.repositories import auth as auth_repository
from app.security import create_access_token, verify_password


def login(
    user,
    connection: Connection,
):
    existing_user = auth_repository.get_user_by_email(
        connection=connection,
        email=user.email,
    )

    if not existing_user or not verify_password(
        user.password,
        existing_user[2],
    ):
        raise HTTPException(
            status_code=401,
            detail="Email or password is incorrect",
        )

    access_token = create_access_token(
        data={"sub": str(existing_user[0])},
        expires_delta=timedelta(minutes=30),
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }