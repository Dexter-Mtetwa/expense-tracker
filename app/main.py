from datetime import timedelta

from fastapi import Depends, FastAPI, HTTPException, APIRouter
from psycopg import Connection

from app.db.database import get_db
from app.schemas.users import UserLogin, Token
from app.security import (verify_password, create_access_token)

from app.routers.expenses import router as expenses_router
from app.routers.categories import router as categories_router
from app.routers.users import router as users_router


app = FastAPI()
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(expenses_router)
api_router.include_router(categories_router)
api_router.include_router(users_router)



@app.get('/')
def root():
    return {'message': 'Expense Tracker API'}


@app.get('/health')
def health_check():
    return {'status': 'ok'}


# login user
@api_router.post('/login', response_model=Token)
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






# Database test endpoint
@api_router.get('/db-test')
def db_test(connection: Connection = Depends(get_db)):
    with connection.cursor() as cursor:
        cursor.execute('SELECT 1')
        result = cursor.fetchone()

    return {'db_test_result': result[0]}


app.include_router(api_router)