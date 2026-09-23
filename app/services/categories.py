from fastapi import HTTPException
from psycopg import Connection
import psycopg


# Create a category
def create_category(
    category,
    connection: Connection,
    user_id,
):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO categories (name, creator)
                VALUES (%s, %s)
                RETURNING id, name, created_at;
                """,
                (category.name, user_id),
            )

            created_category = cursor.fetchone()

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


# Get all categories
def get_categories(
    connection: Connection,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, created_at
            FROM categories
            ORDER BY name;
            """
        )

        categories = cursor.fetchall()

    return [
        {
            "id": str(category[0]),
            "name": category[1],
            "created_at": category[2],
        }
        for category in categories
    ]


# Get a specific category by ID
def get_category(
    category_id,
    connection: Connection,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, created_at
            FROM categories
            WHERE id = %s;
            """,
            (category_id,),
        )

        category = cursor.fetchone()

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


# Update a specific category by ID
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

    # Check if the category is in use before updating the name
    if "name" in updates:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                SELECT 1
                FROM expenses
                WHERE category_id = %s
                LIMIT 1;
                """,
                (category_id,),
            )

            category_in_use = cursor.fetchone()

        if category_in_use:
            raise HTTPException(
                status_code=409,
                detail="Category is in use",
            )

    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE categories
                SET name = %s
                WHERE id = %s
                AND creator = %s
                RETURNING id, name, created_at;
                """,
                (
                    updates["name"],
                    category_id,
                    user_id,
                ),
            )

            updated_category = cursor.fetchone()

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


# Delete a specific category by ID
def delete_category(
    category_id,
    user_id,
    connection: Connection,
):
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                DELETE FROM categories
                WHERE id = %s
                AND creator = %s
                RETURNING id;
                """,
                (category_id, user_id),
            )

            deleted_category = cursor.fetchone()

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
