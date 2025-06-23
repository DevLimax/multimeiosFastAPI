from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from models.book_model import BookModel
from models.review_model import BookReview
from schemas.review_schema import ReviewSchemaBase, ReviewSchemaUpdate

from core.deps import get_session, get_current_user
from utils.search_in_db import search_item_in_db

router = APIRouter()

#GET All Reviews
@router.get("/", response_model=List[ReviewSchemaBase])
async def get_reviews(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(BookReview).order_by(BookReview.id)
        result = await session.execute(query)
        reviews: List[BookReview] = result.scalars().all()
        return reviews
    
#GET Review By ID
@router.get("/{review_id}", response_model=ReviewSchemaBase)
async def get_review(review_id: int, db: AsyncSession = Depends(get_session)):
    review = search_item_in_db(id=review_id, Model=BookReview, db=db)

    if not review:
        raise HTTPException(detail="Avaliação não encontrada")
    
    return review

#POST Review
@router.post("/",  response_model=ReviewSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_review(review: ReviewSchemaBase, 
                        db: AsyncSession = Depends(get_session), 
                        current_user: UserModel = Depends(get_current_user)
):  
    new_review = BookReview(
        book_id = review.book_id,
        user_id = current_user.id,
        comment = review.comment,
        rating = review.rating
    )

    async with db as session:
        try:
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except IntegrityError:
            raise HTTPException(detail="Erro ja éxiste uma avaliação do usúario para esse livro.", status_code=status.HTTP_409_CONFLICT)

