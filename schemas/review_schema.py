from typing import Optional, List
from pydantic import BaseModel, EmailStr

class ReviewSchemaBase(BaseModel):
    id: Optional[int] = None
    book: int
    user: int 
    comment: Optional[str] = None
    rating: float

    class Config:
        from_attributes = True

class ReviewSchemaUpdate(BaseModel):
    book: Optional[int] = None
    user: Optional[int] = None 
    comment: Optional[str] = None
    rating: Optional[float] = None