import psycopg

from psycopg import Connection


def get_expenses(
    connection: Connection,
    user_id,
    category_id=None,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description, amount, date, created_at, category_id
            FROM expenses
            WHERE user_id = %s
            AND (%s::uuid IS NULL OR category_id = %s::uuid)
            ORDER BY date DESC, created_at DESC;
            """,
            (user_id, category_id, category_id),
        )
        return cursor.fetchall()


def create_expense(
    connection: Connection,
    expense,
    user_id,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO expenses (
                name,
                description,
                amount,
                date,
                user_id,
                category_id
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id, name, description, amount, date, created_at, category_id;
            """,
            (
                expense.name,
                expense.description,
                expense.amount,
                expense.date,
                user_id,
                expense.category_id,
            ),
        )
        return cursor.fetchone()


def get_total_spent(
    connection: Connection,
    user_id,
    category_id=None,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT COALESCE(SUM(amount), 0)
            FROM expenses
            WHERE user_id = %s
            AND (%s::uuid IS NULL OR category_id = %s::uuid);
            """,
            (user_id, category_id, category_id),
        )
        return cursor.fetchone()[0]


def get_expense(
    connection: Connection,
    expense_id,
    user_id,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, name, description, amount, date, created_at, category_id
            FROM expenses
            WHERE id = %s
            AND user_id = %s;
            """,
            (expense_id, user_id),
        )
        return cursor.fetchone()


def update_expense(
    connection: Connection,
    expense_id,
    expense,
    user_id,
):
    updates = expense.model_dump(exclude_unset=True)

    set_clauses = []
    values = []

    for field, value in updates.items():
        set_clauses.append(f"{field} = %s")
        values.append(value)

    values.extend([expense_id, user_id])

    query = f"""
        UPDATE expenses
        SET {", ".join(set_clauses)}
        WHERE id = %s
        AND user_id = %s
        RETURNING id, name, description, amount, date, created_at, category_id;
    """

    with connection.cursor() as cursor:
        cursor.execute(query, values)
        return cursor.fetchone()


def delete_expense(
    connection: Connection,
    expense_id,
    user_id,
):
    with connection.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM expenses
            WHERE id = %s
            AND user_id = %s
            RETURNING id;
            """,
            (expense_id, user_id),
        )
        return cursor.fetchone()