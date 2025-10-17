
from typing import Optional, List, Union
from fastapi import Form
from pydantic import BaseModel, EmailStr, ConfigDict
from typing_extensions import Annotated, Doc
from datetime import datetime
from .review_serializer import ReviewSchemaBase
from .genre_serializer import GenreSchemaBase

class ReviewToBookSchema(BaseModel):
    id: Optional[int] = None
    user_id: int
    comment: Optional[str] = None
    rating: int
    created_at: datetime

#=======================================
class BookSchemaBase(BaseModel):
    id: Optional[int] = None
    added_by_id: Optional[int] = None
    title: str
    author: str
    synopsis: Optional[str] = None
    cover: Optional[str] = None
    genre: GenreSchemaBase
    genre_two: Optional[GenreSchemaBase] = None
    quantity: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(
        from_attributes=True
    )

class BookSchemaReviews(BookSchemaBase):
    reviews: Optional[List[ReviewToBookSchema]] = None

    model_config = ConfigDict(
        from_attributes=True
    )

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
        self.synopsis = synopsis.title( ) if synopsis else None
        self.genre = genre
        self.genre_two = genre_two
        self.quantity = quantity
    
