from typing import Optional, List, Union
from fastapi import Form
from pydantic import Field, field_serializer
from pydantic import BaseModel, EmailStr
from typing_extensions import Annotated, Doc
from datetime import datetime
from schemas.review_schema import ReviewSchemaBase
from schemas.bookLoan_schema import BookLoanSchemaBase
from schemas.loanRequest_schema import RequestLoanSchemaBase


class BookSchemaBase(BaseModel):
    id: int
    added_by_id: int
    title: str
    author: str
    synopsis: Optional[str] = None
    cover: str
    genre_id: int
    genre_two_id: Optional[int] = None
    quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class BookSchemaWithExtras(BookSchemaBase):    
    reviews: Optional[List[ReviewSchemaBase]] = None
    loans: Optional[List[BookLoanSchemaBase]] = None
    requestLoans: Optional[List[RequestLoanSchemaBase]] = None

    class Config:
        from_attributes = True
        
class BookSchemaForLoan(BaseModel):
    id: int
    cover: str
    title: str
    author: str
    genre: int
    genre_two: Optional[int] = None
    quantity: int
    synopsis: Optional[str] = None
        
class BookSchemaForm:
    def __init__(
        self,
        title: Annotated[str, Form()],
        author: Annotated[str, Form()],
        genre: Annotated[int, Form()],
        quantity: Annotated[int, Form()],
        genre_two: Annotated[Union[int, None], Form()] = None,
        synopsis: Annotated[Union[str, None], Form()] = None
):
        self.title = title.title()
        self.author = author.title()
        self.synopsis = synopsis.title( ) if synopsis else None
        self.genre = genre
        self.genre_two = genre_two
        self.quantity = quantity

class BookSchemaUpdateForm():
    def __init__(
        self,
        title: Annotated[Union[str, None], Form()] = None,
        author: Annotated[Union[str, None], Form()] = None,
        synopsis: Annotated[Union[str, None], Form()] = None,
        genre: Annotated[Union[int, None], Form()] = None,
        genre_two: Annotated[Union[int, None], Form()] = None,
        quantity: Annotated[Union[int, None], Form()] = None,
        is_active: Annotated[Union[bool, None], Form()] = None
    ):
        self.title = title.title() if title else None
        self.author = author .title() if author else None
        self.synopsis = synopsis .title() if synopsis else None
        self.genre_id = genre
        self.genre_two_id = genre_two
        self.quantity = quantity
        self.is_active = is_active
    


    