
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from psycopg import Connection

from app.db.database import get_db
from app.schemas.users import UserLogin, Token
from app.security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["Authentication"])

# login user
@router.post('/login', response_model=Token)
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