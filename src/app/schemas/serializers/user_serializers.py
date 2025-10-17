from typing import Optional, List, Annotated, Union
from fastapi import Form
from pydantic import BaseModel, EmailStr, ConfigDict
from datetime import datetime

class _BookToUserSchemas(BaseModel):
    id: int
    title: str
    author: str
    cover: str
class _ReviewSchemaToUser(BaseModel):
    id: int
    book: _BookToUserSchemas
    comment: Optional[str] = None
    rating: float   
    created_at: datetime

class _LoanSchemaToUser(BaseModel):
    id: int
    book: _BookToUserSchemas
    status: str
    unique_book_code_: Optional[int] = None
    loan_date: Optional[datetime] = None 
    return_date: Optional[datetime] = None 
    updated_at: Optional[datetime] = None 
    is_active: Optional[bool] = None
    
class _RequestLoanSchemaToUser(BaseModel):
    id: int
    book: _BookToUserSchemas
    status: str
    created_at: datetime
    updated_at: datetime
    is_active: bool

#=======================================================
class UserSchemaBase(BaseModel):
    id: Optional[int] = None
    is_admin: bool
    last_login: Optional[datetime] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enrollment: Optional[int] = None
    email: EmailStr
    profile_image: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(
        from_attributes=True
    )

class UserSchemaWithExtras(UserSchemaBase):
    reviews: Optional[List[_ReviewSchemaToUser]] = None
    loans: Optional[List[_LoanSchemaToUser]] = None
    requestLoans: Optional[List[_RequestLoanSchemaToUser]] = None

class UserSchemaCreateForm:
    def __init__(
        self,
        #Campos Obrigatórios
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
        first_name: Annotated[str, Form()],
        last_name: Annotated[str, Form()],
        
        #Campos Opcionais
        enrollment: Annotated[Union[int, None],Form()] = None,
        is_admin: Annotated[Union[bool, None], Form()] = None,
    ):
        self.first_name = first_name.title()
        self.last_name = last_name.title()
        self.email = email
        self.password = password
        self.enrollment = enrollment if enrollment else None
        self.is_admin = is_admin if is_admin else False

class UserSchemaUpdateForm:
    def __init__(
        self,
        email: Annotated[Union[EmailStr, None], Form()] = None,
        password: Annotated[Union[str, None], Form()] = None,
        first_name: Annotated[Union[str, None], Form()] = None,
        last_name: Annotated[Union[str, None], Form()] = None,
        enrollment: Annotated[Union[int, None],Form()] = None,
        is_admin: Annotated[Union[bool, None], Form()] = None,
        is_active: Annotated[Union[bool, None], Form()] = None
    ):
        self.first_name = first_name.title() if first_name else None
        self.last_name = last_name.title() if last_name else None
        self.email = email
        self.password = password
        self.enrollment = enrollment
        self.is_admin = is_admin
        self.is_active = is_active
    