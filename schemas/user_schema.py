from typing import Optional, List, Annotated, Union
from fastapi import Form
from pydantic import BaseModel, EmailStr, field_serializer
from .review_schema import ReviewSchemaBase
from .bookLoan_schema import BookLoanSchemaBase
from .loanRequest_schema import RequestLoanSchemaBase
from datetime import datetime

class UserSchemaBase(BaseModel):
    id: Optional[int] = None
    is_admin: bool
    last_login: Optional[datetime] = None
    username: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    enrollment: Optional[int] = None
    email: EmailStr
    profile_image: Optional[str] = None
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("created_at", "updated_at", "last_login", when_used="always")
    def serialize_datetime(self, value: Optional[datetime]) -> Optional[str]:
        if value:
            return value.strftime("%d/%m/%Y %H:%M")
        return None
    class Config:
        from_attributes = True

class UserSchemaWithExtras(UserSchemaBase):
    reviews: Optional[List[ReviewSchemaBase]] = None
    loans: Optional[List[BookLoanSchemaBase]] = None
    requestLoans: Optional[List[RequestLoanSchemaBase]] = None

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
    


