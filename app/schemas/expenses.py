from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    name: str
    description: str | None = None
    amount: Decimal = Field(gt=0)
    date: date
    category_id: str


class ExpenseResponse(BaseModel):
    id: str
    name: str
    description: str | None
    amount: Decimal
    date: date
    created_at: datetime
    category_id: str