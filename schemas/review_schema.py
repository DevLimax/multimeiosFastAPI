from typing import Optional, List
from pydantic import BaseModel, EmailStr, field_serializer
from datetime import datetime

class ReviewSchemaBase(BaseModel):
    id: Optional[int] = None
    book_id: int
    user_id: Optional[int] = None 
    comment: Optional[str] = None
    rating: float
    created_at: datetime = None

    @field_serializer("created_at", when_used="always")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.strftime("%d/%m/%Y %H:%M")
        return None

    class Config:
        from_attributes = True

class ReviewSchemaUpdate(BaseModel):
    book: Optional[int] = None
    user: Optional[int] = None 
    comment: Optional[str] = None
    rating: Optional[float] = None
    
class ReviewSchemaCreate(BaseModel):
    book_id: int
    comment: Optional[str] = None
    rating: float