from typing import Optional
from pydantic import BaseModel
from datetime import datetime

class BookLoanSchemaBase(BaseModel):
    id: Optional[int] = None
    book_id: int
    user_id: int
    status: str
    loan_date: datetime
    return_date: datetime
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class BookLoanSchemaUpdate(BookLoanSchemaBase):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 