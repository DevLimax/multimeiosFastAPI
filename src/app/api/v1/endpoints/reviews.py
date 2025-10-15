from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.models.user_model import UserModel
from app.models.book_model import BookModel
from app.models.review_model import BookReview
from app.schemas.serializers.review_serializer import ReviewSchemaBase, ReviewSchemaUpdate, ReviewSchemaCreate

from app.core.deps import get_session, get_current_user
from app.utils.querys_db import search_item_in_db, search_all_itens_in_db
from app.utils.exceptions import NotFoundException, UniqueViolationException, NotPermissionsException, InternalServerException

router = APIRouter()

#GET All Reviews
@router.get("/", response_model=List[ReviewSchemaBase])
async def get_reviews(db: AsyncSession = Depends(get_session)):
    async with db as session:
        reviews = await search_all_itens_in_db(session=session, Model=BookReview)
        return reviews
    
#GET Review By ID
@router.get("/{id}", response_model=ReviewSchemaBase)
async def get_review(id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        review = await search_item_in_db(id=id, Model=BookReview, session=session)

        if not review:
            raise NotFoundException(id) 
        
        return review

#POST Review
@router.post("/",  response_model=ReviewSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_review(data: ReviewSchemaCreate, 
                        db: AsyncSession = Depends(get_session), 
                        current_user: UserModel = Depends(get_current_user)
):  
    new_review = BookReview(**data.dict(exclude_unset=True), user_id=current_user.id)

    if new_review.rating > 5 or new_review.rating <= 0:
        raise HTTPException(detail="A nota para avaliação deve estar entre 1 e 5, exemplo: 4.8", status_code=status.HTTP_403_FORBIDDEN)
    
    async with db as session:
        try:
            session.add(new_review)
            await session.commit()
            await session.refresh(new_review)
            return new_review
        except IntegrityError as e:
            if "uniqueviolation" in str(e.orig).lower():
                raise UniqueViolationException(error=e)
            else:
                raise HTTPException(detail=f"Erro de integridade: {e.orig}", status_code=status.HTTP_409_CONFLICT)
        
        except Exception as e:
            raise InternalServerException()
    
#DELETE Review
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise NotPermissionsException(id)
    
    async with db as session:
        review = await search_item_in_db(id=id, session=session, Model=BookReview)
        if not review:
            raise NotFoundException(id)

        try:
            
            await session.delete(review)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        
        except Exception as e:
            raise InternalServerException()