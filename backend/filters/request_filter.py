from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum
from models.loanRequest_model import Status

class RequestsFilter(BaseModel):
    book_id: Optional[int] = None
    user_id: Optional[int] = None
    status: Optional[Status] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None