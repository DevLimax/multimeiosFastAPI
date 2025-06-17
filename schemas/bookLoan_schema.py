from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BookLoanSchemaBase(BaseModel):
    id: Optional[int] = None
    book: int
    user: int
    status: str
    loan_date: datetime
    return_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookLoanSchemaUpdate(BookLoanSchemaBase):
    book: Optional[int] = None
    user: Optional[int] = None
    status: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 