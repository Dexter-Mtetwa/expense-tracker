from datetime import datetime

from pydantic import BaseModel


class CategoryCreate(BaseModel):
    name: str


class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime


class CategoryUpdate(BaseModel):
    name: str | None = None