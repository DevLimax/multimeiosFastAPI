from typing import Optional, List, Annotated, Union
from fastapi import Form
from pydantic import BaseModel, EmailStr
from .review_schema import ReviewSchemaBase
from .bookLoan_schema import BookLoanSchemaBase
from .loanRequest_schema import LoanSchemaBase
from datetime import datetime

class UserSchemaBase(BaseModel):
    id: Optional[int] = None
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enrollment: Optional[int] = None
    email: EmailStr
    is_admin: bool
    profile_image: Optional[str] = None
    last_login: Optional[datetime] = None
    is_active: bool

    class Config:
        from_attributes = True

class UserSchemaWithExtras(UserSchemaBase):
    reviews: Optional[List[ReviewSchemaBase]] = None
    loans: Optional[List[BookLoanSchemaBase]] = None
    requestLoans: Optional[List[LoanSchemaBase]] = None

class UserSchemaCreateForm:
    def __init__(
        self,
        username: Annotated[str, Form()],
        email: Annotated[EmailStr, Form()],
        password: Annotated[str, Form()],
        first_name: Annotated[Union[str, None], Form()] = None,
        last_name: Annotated[Union[str, None], Form()] = None,
        enrollment: Annotated[Union[int, None],Form()] = None,
        is_admin: Annotated[Union[bool, None], Form()] = None,
    ):
        self.username = username
        self.first_name = first_name.title() if first_name else None
        self.last_name = last_name.title() if last_name else None
        self.email = email
        self.password = password
        self.enrollment = enrollment
        self.is_admin = is_admin

class UserSchemaUpdateForm:
    def __init__(
        self,
        username: Annotated[Union[str, None], Form()] = None,
        email: Annotated[Union[EmailStr, None], Form()] = None,
        password: Annotated[Union[str, None], Form()] = None,
        first_name: Annotated[Union[str, None], Form()] = None,
        last_name: Annotated[Union[str, None], Form()] = None,
        enrollment: Annotated[Union[int, None],Form()] = None,
        is_admin: Annotated[Union[bool, None], Form()] = None,
        is_active: Annotated[Union[bool, None], Form()] = None
    ):
        self.username = username
        self.first_name = first_name.title() if first_name else None
        self.last_name = last_name.title() if last_name else None
        self.email = email
        self.password = password
        self.enrollment = enrollment
        self.is_admin = is_admin
        self.is_active = is_active
    


