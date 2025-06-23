from typing import Optional, List, Union
from fastapi import Form
from pydantic import Field
from pydantic import BaseModel, EmailStr
from typing_extensions import Annotated, Doc
from datetime import datetime

class BookSchemaBase(BaseModel):
    id: Optional[int] = None
    title: str
    author: str
    synopsis: Optional[str] = None
    cover: Optional[str] = None
    genre_id: int
    genre_two_id: Optional[int] = None
    quantity: int
    created_at: datetime
    added_by: Optional[int] = None
    is_active: bool

    class Config:
        from_attributes = True


class BookSchemaReviews(BookSchemaBase):
    reviews: Optional[List[int]] = None

    class Config:
        from_attributes = True

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
        self.synopsis = synopsis.title( ) if title else None
        self.genre = genre
        self.genre_two = genre_two
        self.quantity = quantity
    