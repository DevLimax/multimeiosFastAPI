from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class BookFilter(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre_id: Optional[int] = None
    genre_two_id: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None