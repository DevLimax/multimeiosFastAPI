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

from core.deps import get_session, get_current_user

router = APIRouter()

#GET All Genres
@router.get("/", response_model=List[GenreSchemaBase], status_code=status.HTTP_200_OK)
async def get_genres(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(GenreModel).order_by(GenreModel.id)
        result = await session.execute(query)
        genres = result.scalars().unique().all()
        return genres
    
#GET Genre by ID
@router.get("/{genre_id}", response_model=GenreSchemaBase, status_code=status.HTTP_200_OK)
async def get_genre(genre_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(GenreModel).filter(GenreModel.id == genre_id)
        result = await session.execute(query)
        genre = result.scalars().unique().one_or_none()
        if not genre:
            raise HTTPException(detail="Gênero não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        return genre

#POST Genre
@router.post("/", response_model=GenreSchemaBase, status_code=status.HTTP_201_CREATED)
async def post_genre(genre: GenreSchemaBase,
                     db: AsyncSession = Depends(get_session),
                     current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        if not current_user.is_admin:
            raise HTTPException(detail="Usuário não tem permissão para criar gêneros", status_code=status.HTTP_401_UNAUTHORIZED)

        new_genre = GenreModel(
            name=genre.name.title(),
        )
        try:
            session.add(new_genre)
            await session.commit()
            await session.refresh(new_genre)
            return new_genre
        except IntegrityError:
            await session.rollback()
            raise HTTPException(detail="Gênero já existe", status_code=status.HTTP_409_CONFLICT)

#UPDATE Genre
@router.put("/{genre_id}", response_model=GenreSchemaBase, status_code=status.HTTP_200_OK)
async def put_genre(genre_id: int,
                    genre: GenreSchemaUpdate,
                    db: AsyncSession = Depends(get_session),
                    current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        if not current_user.is_admin:
            raise HTTPException(detail="Usuário não tem permissão para alterar gêneros", status_code=status.HTTP_401_UNAUTHORIZED)
        
        query = select(GenreModel).filter(GenreModel.id == genre_id)
        result = await session.execute(query)
        genre_up = result.scalar_one_or_none()

        if not genre_up:
            raise HTTPException(detail="Gênero não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        if genre.name:
            genre_up.name = genre.name

        session.commit()
        session.refresh(genre_up)
        return genre_up
    
#DELETE Genre
@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: int,
                       db: AsyncSession = Depends(get_session)
):
    async with db as session:
        query = select(GenreModel).filter(GenreModel.id == genre_id)
        result = await session.execute(query)
        genre = result.scalars().unique().one_or_none()

        if not genre:
            raise HTTPException(detail="Gênero não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        await session.delete(genre)
        await session.commit()
        print(f"Gênero {genre_id} - {genre.name} deletado com sucesso")
        return Response(status_code=status.HTTP_204_NO_CONTENT)
