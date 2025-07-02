from typing import Optional
from pydantic import BaseModel, field_serializer, validator
from datetime import datetime
from models.bookloan_model import Status

class BookLoanSchemaBase(BaseModel):    
    id: int
    book_id: int
    user_id: int
    status: Status
    book_code: str
    loan_date: Optional[datetime] = None 
    return_date: Optional[datetime] = None 
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

class BookLoanSchemaCreate(BaseModel):
    book_id: int
    user_id: int
    status: Optional[str] = None
    book_code: str
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 

class BookLoanSchemaUpdate(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    book_code: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 
    is_active: Optional[bool] = None

