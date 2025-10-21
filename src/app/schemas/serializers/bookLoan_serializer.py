from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime
from app.models.loan_model import Status

class BookLoanSchemaBase(BaseModel):
    id: Optional[int] = None
    book_id: int
    user_id: int
    status: str
    unique_book_code: Optional[str] = None
    loan_date: Optional[datetime] = None 
    return_date: Optional[datetime] = None 
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None 
    is_active: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)

class BookLoanSchemaCreate(BookLoanSchemaBase):
    book_id: int
    user_id: int
    status: Optional[str] = None
    unique_book_code: str
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 

class BookLoanSchemaUpdate(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    unique_book_code: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 

