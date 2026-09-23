from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db.database import get_db
from app.schemas.users import UserCreate, UserResponse
from app.services.users import create_user as create_user_service

router = APIRouter(prefix="/users", tags=["Users"])


# create user
@router.post('', response_model=UserResponse, status_code=201)
def create_user_endpoint(user: UserCreate, connection: Connection = Depends(get_db)):
    return create_user_service(user=user, connection=connection)


