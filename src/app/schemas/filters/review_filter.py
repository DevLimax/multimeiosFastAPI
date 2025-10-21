from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class ReviewFilter(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    min_rating: Optional[int] = None
    max_rating: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None