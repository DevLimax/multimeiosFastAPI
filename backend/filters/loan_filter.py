from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.bookloan_model import Status

class LoansFilter(BaseModel):   
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    
    