from datetime import date as Date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    name: str
    description: str | None = None
    amount: Decimal = Field(gt=0)
    date: Date
    category_id: str


class ExpenseResponse(BaseModel):
    id: str
    name: str
    description: str | None
    amount: Decimal
    date: Date
    created_at: datetime
    category_id: str


class ExpenseUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    amount: Decimal | None = Field(default=None, gt=0)
    date: Date | None = None
    category_id: str | None = None