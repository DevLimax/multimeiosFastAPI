from typing import Optional, List
from pydantic import BaseModel, EmailStr

class UserSchemaBase(BaseModel):
    id: Optional[int] = None
    first_name: str 
    last_name: str
    enrrolment: Optional[int] = None
    email: EmailStr
    is_admin: bool = False
    profile_image: Optional[str] = None

    class Config:
        from_attributes = True

class UserSchemaCreate(UserSchemaBase):
    password: str

class UserSchemaUpdate(UserSchemaBase):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enrrolment: Optional[int] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    profile_image: Optional[str] = None

