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