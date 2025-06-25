from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime
from .review_schema import ReviewSchemaBase
from models.loanRequest_model import Status

class LoanSchemaBase(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    book_id: int
    user_id: Optional[int] = None
    status: Optional[Status] = None
    changer_by: Optional[int] = None
    is_active: Optional[bool] = None

class LoanSchemaUpdate(LoanSchemaBase):
    updated_at: Optional[datetime] = None
    book_id: Optional[int] = None
