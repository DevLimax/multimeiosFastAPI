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
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None 

    class Config:
        from_attributes = True

class BookLoanSchemaCreate(BookLoanSchemaBase):
    book_id: int
    book_user: int
    status: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 

class BookLoanSchemaUpdate(BookLoanSchemaBase):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 