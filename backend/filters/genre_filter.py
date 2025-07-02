from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class GenreFilter(BaseModel):
    name: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    