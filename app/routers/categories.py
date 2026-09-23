from fastapi import APIRouter, Depends
from psycopg import Connection

from app.db.database import get_db
from app.dependencies import get_current_user
from app.schemas.categories import CategoryCreate, CategoryResponse, CategoryUpdate

from app.services.categories import (
    create_category as create_category_service,
    get_categories as get_categories_service,
    get_category as get_category_service,
    update_category as update_category_service,
    delete_category as delete_category_service
)

router = APIRouter(prefix="/categories", tags=["Categories"])


# ---category oriented endpoints---
@router.post("", response_model=CategoryResponse, status_code=201)
def create_category_endpoint(
    category: CategoryCreate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return create_category_service(
        category=category,
        connection=connection,
        user_id=user_id,
    )


# Get all categories
@router.get("", response_model=list[CategoryResponse])
def get_categories_endpoint(
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    return get_categories_service(
        connection=connection,
    )


# Get a specific category by ID
@router.get("/{category_id}", response_model=CategoryResponse)
def get_category_endpoint(
    category_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    return get_category_service(
        category_id=category_id,
        connection=connection,
    )


# Update a specific category by ID
@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category_endpoint(
    category_id: str,
    category: CategoryUpdate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return update_category_service(
        category_id=category_id,
        category=category,
        user_id=user_id,
        connection=connection,
    )


# Delete a specific category by ID
@router.delete("/{category_id}", status_code=204)
def delete_category_endpoint(
    category_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return delete_category_service(
        category_id=category_id,
        user_id=user_id,
        connection=connection,
    )
