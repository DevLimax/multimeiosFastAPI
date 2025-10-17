from pydantic import BaseModel
from typing import Optional

class BookFilter(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    genre: Optional[int] = None
    is_active: Optional[bool] = None
    