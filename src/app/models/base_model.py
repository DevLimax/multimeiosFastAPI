from sqlmodel import Field, SQLModel, func

from datetime import datetime

class BaseModel(SQLModel, table=False):
        
    created_at: datetime = Field(default=datetime.now(), nullable=False)
    updated_at: datetime = Field(default=datetime.now(), nullable=False)
    is_active: bool = Field(default=True, nullable=False)