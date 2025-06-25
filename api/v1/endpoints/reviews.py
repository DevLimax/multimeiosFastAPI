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
from utils.search_in_db import search_item_in_db, search_all_itens_in_db
from utils.exceptionsHttp import not_found, unauthorized, exception_not_identified, user_book_conflict

router = APIRouter()

#GET All Reviews
@router.get("/", response_model=List[ReviewSchemaBase])
async def get_reviews(db: AsyncSession = Depends(get_session)):
    async with db as session:
        reviews = await search_all_itens_in_db(db=session, Model=BookReview)
        return reviews
    
#GET Review By ID
@router.get("/{review_id}", response_model=ReviewSchemaBase)
async def get_review(review_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        review = await search_item_in_db(id=review_id, Model=BookReview, db=session)

        if not review:
            not_found() 
        
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

    if new_review.rating > 5 or new_review.rating <= 0:
        raise HTTPException(detail="A nota para avaliação deve estar entre 1 e 5, exemplo: 4.8", status_code=status.HTTP_403_FORBIDDEN)
    
    async with db as session:
        try:
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except IntegrityError:
            user_book_conflict(tablename=BookReview.__tablename__)
        except Exception as e:
            exception_not_identified(error=e)
    
#DELETE Review
@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(review_id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()
    
    async with db as session:
        review = await search_item_in_db(id=review_id, db=session, Model=BookReview)
        if not review:
            not_found()

        try:
            await session.delete(review)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            exception_not_identified(error=e)




