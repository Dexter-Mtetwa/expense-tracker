import psycopg
from fastapi import HTTPException
from psycopg import Connection

from app.repositories import categories as category_repository


def create_category(
    category,
    connection: Connection,
    user_id,
):
    try:
        # outsourced the service layer to the repository layer to keep the service layer clean and focused on business logic
        created_category = category_repository.create_category(
            connection=connection,
            category=category,
            user_id=user_id,
        )
        connection.commit()
    except psycopg.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category already exists",
        )

    return {
        "id": str(created_category[0]),
        "name": created_category[1],
        "created_at": created_category[2],
    }


def get_categories(
    connection: Connection,
):
    categories = category_repository.get_categories(
        connection=connection,
    )

    return [
        {
            "id": str(category[0]),
            "name": category[1],
            "created_at": category[2],
        }
        for category in categories
    ]


def get_category(
    category_id,
    connection: Connection,
):
    category = category_repository.get_category(
        connection=connection,
        category_id=category_id,
    )

    if not category:
        raise HTTPException(
            status_code=404,
            detail="Category not found",
        )

    return {
        "id": str(category[0]),
        "name": category[1],
        "created_at": category[2],
    }


def update_category(
    category_id,
    category,
    user_id,
    connection: Connection,
):
    updates = category.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

    if "name" in updates:
        category_in_use = category_repository.is_category_in_use(
            connection=connection,
            category_id=category_id,
        )

        if category_in_use:
            raise HTTPException(
                status_code=409,
                detail="Category is in use",
            )

    try:
        updated_category = category_repository.update_category(
            connection=connection,
            category_id=category_id,
            name=updates["name"],
            user_id=user_id,
        )

        if not updated_category:
            connection.rollback()
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        connection.commit()

    except psycopg.errors.UniqueViolation:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category already exists",
        )

    return {
        "id": str(updated_category[0]),
        "name": updated_category[1],
        "created_at": updated_category[2],
    }


def delete_category(
    category_id,
    user_id,
    connection: Connection,
):
    try:
        deleted_category = category_repository.delete_category(
            connection=connection,
            category_id=category_id,
            user_id=user_id,
        )

        if not deleted_category:
            connection.rollback()
            raise HTTPException(
                status_code=404,
                detail="Category not found",
            )

        connection.commit()

    except psycopg.errors.ForeignKeyViolation:
        connection.rollback()
        raise HTTPException(
            status_code=409,
            detail="Category is in use",
        )