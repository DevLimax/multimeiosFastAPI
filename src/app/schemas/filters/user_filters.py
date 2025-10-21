from pydantic import BaseModel
from typing import Optional

class UserFilter(BaseModel):
    name: Optional[str] = None
    enrollment: Optional[int] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None
    
