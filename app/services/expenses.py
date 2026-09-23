import psycopg
from psycopg import Connection
from fastapi import HTTPException


# Get all expenses for the current user
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

        expenses = cursor.fetchall()

    return [
        {
            "id": str(expense[0]),
            "name": expense[1],
            "description": expense[2],
            "amount": expense[3],
            "date": expense[4],
            "created_at": expense[5],
            "category_id": str(expense[6]),
        }
        for expense in expenses
    ]


# create an expense
def create_expense(
    expense,
    connection: Connection,
    user_id,
):

    try:
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

            created_expense = cursor.fetchone()

        connection.commit()

    except psycopg.errors.ForeignKeyViolation:
        connection.rollback()

        raise HTTPException(
            status_code=404,
            detail="Category does not exist",
        )

    return {
        "id": str(created_expense[0]),
        "name": created_expense[1],
        "description": created_expense[2],
        "amount": created_expense[3],
        "date": created_expense[4],
        "created_at": created_expense[5],
        "category_id": str(created_expense[6]),
    }


# Get the total amount spent for the current user, optionally filtered by category
def get_total_spent(
    connection: Connection,
    user_id,
    category_id = None,
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
        total = cursor.fetchone()[0]

    return {"total": total}


# Get a specific expense by ID for the current user
def get_expense(
    expense_id,
    connection: Connection,
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

        expense = cursor.fetchone()

    if not expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    return {
        "id": str(expense[0]),
        "name": expense[1],
        "description": expense[2],
        "amount": expense[3],
        "date": expense[4],
        "created_at": expense[5],
        "category_id": str(expense[6]),
    }


# Update a specific expense by ID for the current user
def update_expense(
    expense_id,
    expense,
    connection: Connection,
    user_id,
):

    updates = expense.model_dump(exclude_unset=True)

    if not updates:
        raise HTTPException(
            status_code=400,
            detail="No fields provided for update",
        )

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

    try:
        with connection.cursor() as cursor:
            cursor.execute(query, values)
            updated_expense = cursor.fetchone()

        if not updated_expense:
            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        connection.commit()

    except psycopg.errors.ForeignKeyViolation:
        connection.rollback()

        raise HTTPException(
            status_code=404,
            detail="Category does not exist",
        )

    return {
        "id": str(updated_expense[0]),
        "name": updated_expense[1],
        "description": updated_expense[2],
        "amount": updated_expense[3],
        "date": updated_expense[4],
        "created_at": updated_expense[5],
        "category_id": str(updated_expense[6]),
    }


# Delete a specific expense by ID for the current user
def delete_expense(
    expense_id,
    connection: Connection,
    user_id,
):

    try:
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

            deleted_expense = cursor.fetchone()

        if not deleted_expense:
            connection.rollback()

            raise HTTPException(
                status_code=404,
                detail="Expense not found",
            )

        connection.commit()

    except psycopg.Error:
        connection.rollback()
        raise
        
