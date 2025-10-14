from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.book_model import BookModel, BookSchemaBase, BookSchemaCreate, BookSchemaUpdate
from app.utils.querys_db import search_item_in_db, search_all_itens_in_db
from app.core.deps import get_session

router = APIRouter()

@router.post(
    "/", 
    response_model=BookSchemaBase, 
    status_code=status.HTTP_201_CREATED
)
async def create_book(
    data: BookSchemaCreate,
    db: AsyncSession = Depends(get_session)
) -> Union[BookSchemaBase, HTTPException]:
    
    new_book = BookModel(**data.dict())
    
    try:
        new_book.validate_data()
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)
        return new_book
    except Exception as e:
        await db.rollback()
        print(e)
        raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)