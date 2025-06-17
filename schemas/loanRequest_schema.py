from typing import Optional, List
from pydantic import BaseModel, EmailStr
from datetime import datetime

class LoanSchemaBase(BaseModel):
    id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    book: int
    user: int
    status: str
    changer_by: Optional[int] = None

class LoanSchemaUpdate(LoanSchemaBase):
    updated_at: Optional[datetime] = None
    book: Optional[int] = None
    user: Optional[int] = None
    status: Optional[str] = None