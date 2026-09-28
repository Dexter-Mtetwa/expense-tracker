from psycopg import Connection


def get_user_by_email(
    connection: Connection,
    email: str,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, email, password_hash, role, created_at
            FROM users
            WHERE email = %s;
            """,
            (email,),
        )
        return cursor.fetchone()