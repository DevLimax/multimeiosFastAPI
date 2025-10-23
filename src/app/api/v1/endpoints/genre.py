from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.user_model import UserModel
from app.models.genre_model import GenreModel
from app.schemas.serializers.genre_serializer import GenreSchemaBase,  GenreSchemaCreate

from app.utils.querys_db import search_all_itens_in_db, search_item_in_db
from app.utils.exceptions import NotFoundException, NotPermissionsException, UniqueViolationException, InternalServerException

from app.core.deps import get_session, get_current_user

router = APIRouter()

#GET All Genres
@router.get("/", response_model=List[GenreSchemaBase], status_code=status.HTTP_200_OK)
async def get(
    db: AsyncSession = Depends(get_session)
):
    
    async with db as session:
        genres = await search_all_itens_in_db(session=session, Model=GenreModel)
        return genres
    
#GET Genre by ID
@router.get("/{id}", response_model=GenreSchemaBase, status_code=status.HTTP_200_OK)
async def get_genre(id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        genre = await search_item_in_db(id=id, session=session, Model=GenreModel)
        if not genre:
            raise NotFoundException(id=id)
        return genre

#POST Genre
@router.post("/", response_model=GenreSchemaBase, status_code=status.HTTP_201_CREATED)
async def post_genre(data: GenreSchemaCreate,
                     db: AsyncSession = Depends(get_session),
                     current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise NotPermissionsException()

    new_genre = GenreModel(
        name = data.name.title(),
    )

    try:
        db.add(new_genre)
        await db.commit()
        await db.refresh(new_genre)
        return new_genre
    
    except IntegrityError as e: 
        await db.rollback()
        raise UniqueViolationException(error=e)
    
    except Exception as e:
        await db.rollback()
        raise InternalServerException()
        
#DELETE Genre
@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int,
                       db: AsyncSession = Depends(get_session)
):
    genre = await search_item_in_db(id=genre_id, session=db, Model=GenreModel)
    if not genre:
        raise NotFoundException(id=id)
        
    await db.delete(genre)
    await db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)