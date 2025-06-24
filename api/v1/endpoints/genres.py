from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from models.genre_model import GenreModel
from schemas.genre_schema import GenreSchemaBase, GenreSchemaUpdate

from utils.search_in_db import *
from utils.exceptionsHttp import not_found, exception_not_identified, unauthorized

from core.deps import get_session, get_current_user

router = APIRouter()

#GET All Genres
@router.get("/", response_model=List[GenreSchemaBase], status_code=status.HTTP_200_OK)
async def get_genres(db: AsyncSession = Depends(get_session)):
    async with db as session:
        genres = await search_all_itens_in_db(db=session, Model=GenreModel)
        return genres
    
#GET Genre by ID
@router.get("/{genre_id}", response_model=GenreSchemaBase, status_code=status.HTTP_200_OK)
async def get_genre(genre_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        genre = await search_item_in_db(id=genre_id, db=session, Model=GenreModel)
        if not genre:
            not_found()
        return genre

#POST Genre
@router.post("/", response_model=GenreSchemaBase, status_code=status.HTTP_201_CREATED)
async def post_genre(genre: GenreSchemaBase,
                     db: AsyncSession = Depends(get_session),
                     current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        unauthorized()

    new_genre = GenreModel(
        name=genre.name.title(),
    )
    try:
        db.add(new_genre)
        await db.commit()
        await db.refresh(new_genre)
        return new_genre
    except IntegrityError:
        await db.rollback()
        raise HTTPException(detail="Gênero já existe", status_code=status.HTTP_409_CONFLICT)
    except Exception as e:
        exception_not_identified(error=e)

#UPDATE Genre
@router.put("/{genre_id}", response_model=GenreSchemaBase, status_code=status.HTTP_200_OK)
async def put_genre(genre_id: int,
                    genre: GenreSchemaUpdate,
                    db: AsyncSession = Depends(get_session),
                    current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        unauthorized()
        
    async with db as session:
        genre_db = search_item_in_db(id=genre_id, db=session, Model=GenreModel)
        if not genre_db:
            raise HTTPException(detail="Gênero não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        for key, value in genre.dict(exclude_unset=True).items():
            if value is not None:
                setattr(genre_db, key, value)
        
        await session.commit()
        await session.refresh(genre_db)
        return genre_db

#DELETE Genre
@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int,
                       db: AsyncSession = Depends(get_session)
):
    async with db as session:
        genre = search_item_in_db(id=genre_id, db=session, Model=GenreModel)
        if not genre:
            not_found()
            
        await session.delete(genre)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
