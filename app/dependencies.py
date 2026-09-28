from uuid import UUID

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from psycopg import Connection

from app.db.database import get_db
from app.repositories import users as user_repository
from app.security import decode_access_token


security = HTTPBearer()


def get_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    return credentials.credentials


def get_token_payload(
    token: str = Depends(get_token),
):
    try:
        return decode_access_token(token)
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user_id(
    payload: dict = Depends(get_token_payload),
):
    user_id = payload.get("sub")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    try:
        return UUID(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


def get_current_user(
    user_id: UUID = Depends(get_current_user_id),
    connection: Connection = Depends(get_db),
):
    user = user_repository.get_user_by_id(
        connection=connection,
        user_id=user_id,
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return user


def require_role(required_role: str):
    def role_dependency(
        user=Depends(get_current_user),
    ):
        if user[2] != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions",
            )

        return user

    return role_dependency