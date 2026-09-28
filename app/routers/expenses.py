from fastapi import APIRouter, Depends
from psycopg import Connection

from app.schemas.expenses import ExpenseResponse
from app.dependencies import get_current_user, get_db
from app.schemas.expenses import ExpenseCreate, ExpenseUpdate

from app.services.expenses import (
    get_expenses as get_expenses_service,
    create_expense as create_expense_service,
    get_total_spent as get_total_spent_service,
    get_expense as get_expense_service,
    update_expense as update_expense_service,
    delete_expense as delete_expense_service
)


router = APIRouter(prefix="/expenses", tags=["Expenses"])


# Get all expenses for the current user
@router.get("", response_model=list[ExpenseResponse])
def get_expenses_endpoint(
    category_id: str | None = None,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    # outsourced the business logic to the service layer to keep the router clean and focused on routing
    return get_expenses_service(
        connection=connection,
        user_id=user_id,
        category_id=category_id,
    )


# create an expense
@router.post("", response_model=ExpenseResponse, status_code=201)
def create_expense_endpoint(
    expense: ExpenseCreate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return create_expense_service(
        connection=connection,
        user_id=user_id,
        expense=expense,
    )


# Get the total amount spent for the current user, optionally filtered by category
@router.get("/total")
def get_total_spent_endpoint(
    category_id: str | None = None,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return get_total_spent_service(
        connection=connection,
        user_id=user_id,
        category_id=category_id,
    )


# Get a specific expense by ID for the current user
@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense_endpoint(
    expense_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return get_expense_service(
        connection=connection,
        user_id=user_id,
        expense_id=expense_id,
    )


# Update a specific expense by ID for the current user
@router.patch("/{expense_id}", response_model=ExpenseResponse)
def update_expense_endpoint(
    expense_id: str,
    expense: ExpenseUpdate,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return update_expense_service(
        connection=connection,
        user_id=user_id,
        expense=expense,
        expense_id=expense_id,
    )


# Delete a specific expense by ID for the current user
@router.delete("/{expense_id}", status_code=204)
def delete_expense_endpoint(
    expense_id: str,
    user=Depends(get_current_user),
    connection: Connection = Depends(get_db),
):
    user_id = user[0]

    return delete_expense_service(
        expense_id=expense_id,
        connection=connection,
        user_id=user_id,
    )