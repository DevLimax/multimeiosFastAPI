from typing import Optional
from pydantic import BaseModel, field_serializer
from datetime import datetime
from app.models.loanRequest_model import Status

class RequestLoanSchemaBase(BaseModel):
    id: Optional[int] = None
    book_id: int
    user_id: Optional[int] = None
    status: Optional[Status] = None
    changer_by: Optional[int] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("created_at", "updated_at", when_used="always")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.strftime("%d/%m/%Y %H:%M")
        return None

class RequestLoanSchemaUpdate(RequestLoanSchemaBase):
    book_id: Optional[int] = None
    unique_book_code: Optional[str] = None

class RequestLoanSchemaCreate(RequestLoanSchemaBase):
    user_id: Optional[int] = None
    book_id: int
    status: Optional[Status] = None