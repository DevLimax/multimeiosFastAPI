from typing import Optional
from pydantic import BaseModel, ConfigDict
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

    model_config = ConfigDict(
        from_attributes=True
    )

class RequestLoanSchemaUpdate(RequestLoanSchemaBase):
    book_id: Optional[int] = None
    unique_book_code: Optional[str] = None

class RequestLoanSchemaCreate(RequestLoanSchemaBase):
    user_id: Optional[int] = None
    book_id: int
    status: Optional[Status] = None