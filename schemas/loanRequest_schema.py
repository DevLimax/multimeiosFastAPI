from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class LoanSchemaBase(BaseModel):
    id: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    book_id: int
    user_id: Optional[int] = None
    status: Optional[str] = None
    changer_by: Optional[int] = None

class LoanSchemaUpdate(LoanSchemaBase):
    updated_at: Optional[datetime] = None
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[str] = None
    changer_by: Optional[int] = None