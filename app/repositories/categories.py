import psycopg
from psycopg import Connection


def create_category(connection: Connection, category, user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO categories (name, creator)
            VALUES (%s, %s)
            RETURNING id, name, created_at;
            """,
            (category.name, user_id),
        )
        return cursor.fetchone()


def get_categories(connection: Connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, created_at
            FROM categories
            ORDER BY name;
            """
        )
        return cursor.fetchall()


def get_category(connection: Connection, category_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, created_at
            FROM categories
            WHERE id = %s;
            """,
            (category_id,),
        )
        return cursor.fetchone()


def is_category_in_use(connection: Connection, category_id):
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
        return cursor.fetchone()


def update_category(connection: Connection, category_id, name, user_id):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            UPDATE categories
            SET name = %s
            WHERE id = %s
            AND creator = %s
            RETURNING id, name, created_at;
            """,
            (name, category_id, user_id),
        )
        return cursor.fetchone()


def delete_category(connection: Connection, category_id, user_id):
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
        return cursor.fetchone()