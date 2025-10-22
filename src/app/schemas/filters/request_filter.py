from pydantic import BaseModel
from typing import Optional
from app.models.loanRequest_model import Status
from datetime import datetime

class RequestFilter(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    
