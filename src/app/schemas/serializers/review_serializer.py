from typing import Optional, List
from pydantic import BaseModel, ConfigDict
from datetime import datetime

class ReviewSchemaBase(BaseModel):
    id: Optional[int] = None
    book_id: int
    user_id: Optional[int] = None 
    comment: Optional[str] = None
    rating: float
    created_at: datetime = None

    model_config = ConfigDict(
        from_attributes=True
    )

class ReviewSchemaUpdate(BaseModel):
    book: Optional[int] = None
    user: Optional[int] = None 
    comment: Optional[str] = None
    rating: Optional[float] = None
    
class ReviewSchemaCreate(BaseModel):
    book_id: int
    comment: Optional[str] = None
    rating: float