from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from uuid import UUID
import jwt

from app.security import decode_access_token
from app.db.database import get_db

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
    connection = Depends(get_db),
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, role, created_at
            FROM users
            WHERE id = %s;
            """,
            (user_id,),
        )
        user = cursor.fetchone()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    return user