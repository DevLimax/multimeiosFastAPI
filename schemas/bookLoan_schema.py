from typing import Optional
from pydantic import BaseModel, field_serializer, validator
from datetime import datetime
from models.bookloan_model import Status

class BookLoanSchemaBase(BaseModel):
    id: Optional[int] = None
    book_id: int
    user_id: int
    status: str
    book_code: Optional[str] = None
    loan_date: Optional[datetime] = None 
    return_date: Optional[datetime] = None 
    created_at: Optional[datetime] = None 
    updated_at: Optional[datetime] = None 
    is_active: Optional[bool] = None

    @field_serializer("loan_date", "return_date", "created_at", "updated_at", when_used="always")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.strftime("%d/%m/%Y %H:%M")
        return None
    
    class Config:
        from_attributes = True

class BookLoanSchemaCreate(BookLoanSchemaBase):
    book_id: int
    user_id: int
    status: Optional[str] = None
    book_code: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 

class BookLoanSchemaUpdate(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    book_code: Optional[str] = None
    loan_date: Optional[datetime] = None
    return_date: Optional[datetime] = None 

