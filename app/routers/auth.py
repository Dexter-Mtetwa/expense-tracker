from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db.database import get_db
from app.schemas.users import UserLogin, Token
from app.services.auth import login as login_service

router = APIRouter(prefix="/auth", tags=["Authentication"])

# login user
@router.post('/login', response_model=Token)
def login_endpoint(user: UserLogin, connection: Connection = Depends(get_db)):
    return login_service(user=user, connection=connection)