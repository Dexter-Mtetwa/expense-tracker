import psycopg

from fastapi import HTTPException
from psycopg import Connection

from app.repositories import expenses as expense_repository


def get_expenses(
    connection: Connection,
    user_id,
    category_id=None,
):
    # outsourced the sql to the repository layer to keep the service layer clean and focused on business logic
    expenses = expense_repository.get_expenses(
        connection=connection,
        user_id=user_id,
        category_id=category_id,
    )

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


def create_expense(
    expense,
    connection: Connection,
    user_id,
):
    try:
        created_expense = expense_repository.create_expense(
            connection=connection,
            expense=expense,
            user_id=user_id,
        )

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


def get_total_spent(
    connection: Connection,
    user_id,
    category_id=None,
):
    total = expense_repository.get_total_spent(
        connection=connection,
        user_id=user_id,
        category_id=category_id,
    )

    return {"total": total}


def get_expense(
    expense_id,
    connection: Connection,
    user_id,
):
    expense = expense_repository.get_expense(
        connection=connection,
        expense_id=expense_id,
        user_id=user_id,
    )

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

    try:
        updated_expense = expense_repository.update_expense(
            connection=connection,
            expense_id=expense_id,
            expense=expense,
            user_id=user_id,
        )

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


def delete_expense(
    expense_id,
    connection: Connection,
    user_id,
):
    deleted_expense = expense_repository.delete_expense(
        connection=connection,
        expense_id=expense_id,
        user_id=user_id,
    )

    if not deleted_expense:
        raise HTTPException(
            status_code=404,
            detail="Expense not found",
        )

    connection.commit()