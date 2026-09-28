from psycopg import Connection


def create_user(
    connection: Connection,
    email: str,
    password_hash: str,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO users (email, password_hash)
            VALUES (%s, %s)
            RETURNING id, email, role, created_at;
            """,
            (email, password_hash),
        )
        return cursor.fetchone()


def get_user_by_id(
    connection: Connection,
    user_id,
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
        return cursor.fetchone()


def get_users(connection: Connection):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, role, created_at
            FROM users
            ORDER BY created_at;
            """
        )
        return cursor.fetchall()