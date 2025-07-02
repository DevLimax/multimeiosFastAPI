from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime
from models.loanRequest_model import Status

class RequestLoanSchemaBase(BaseModel):
    id: int
    book_id: int
    user_id: int
    status: Status
    changer_by_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

class RequestLoanSchemaUpdate(RequestLoanSchemaBase):
    id: Optional[int] = None
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    book_code: Optional[str] = None
    is_active: Optional[bool] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RequestLoanSchemaCreate(BaseModel):
    book_id: int


