from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db.database import get_db
from app.dependencies import require_role
from app.schemas.users import UserCreate, UserListResponse, UserResponse
from app.services.users import create_user as create_user_service
from app.services.users import get_users as get_users_service

router = APIRouter(prefix="/users", tags=["Users"])


# create user
@router.post('', response_model=UserResponse, status_code=201)
def create_user_endpoint(user: UserCreate, connection: Connection = Depends(get_db)):
    return create_user_service(user=user, connection=connection)


@router.get(
    "",
    response_model=list[UserListResponse],
    dependencies=[Depends(require_role("ADMIN"))],
)
def get_users_endpoint(connection: Connection = Depends(get_db)):
    return get_users_service(connection=connection)