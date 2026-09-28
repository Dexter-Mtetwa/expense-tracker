from datetime import date as Date, datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    amount: Decimal = Field(gt=0)
    date: Date
    category_id: UUID

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Name cannot be blank")

        return value


class ExpenseResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    amount: Decimal
    date: Date
    created_at: datetime
    category_id: UUID


class ExpenseUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    amount: Decimal | None = Field(default=None, gt=0)
    date: Date | None = None
    category_id: UUID | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str | None) -> str | None:
        if value is None:
            return None

        value = value.strip()

        if not value:
            raise ValueError("Name cannot be blank")

        return value