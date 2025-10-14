from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.genre_model import GenreModel, GenreSchemaBase, GenreSchemaUpdate
from app.core.deps import get_session
from app.utils.querys_db import search_all_itens_in_db, search_item_in_db

#Bypass warning SQLModel Select
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True
#Bypass end

router = APIRouter()

@router.post("/", response_model=GenreSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_genre(
    data: GenreSchemaBase,
    db: AsyncSession = Depends(get_session)
):
    
    new_genre = GenreModel(**data.dict())
    
    try:
        new_genre.validate_data()
        db.add(new_genre)
        await db.commit()
        await db.refresh(new_genre)
        return new_genre
    except Exception as e:
        await db.rollback()
        print(e)
        raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.get("/", response_model=List[GenreSchemaBase], status_code=status.HTTP_200_OK)
async def get_genres(
    db: AsyncSession = Depends(get_session)
):
    
    genres: Optional[List[GenreModel]] = await search_all_itens_in_db(
        session=db,
        Model=GenreModel
    )
    return genres

@router.get("/{id}", response_model=GenreSchemaBase, status_code=status.HTTP_200_OK)
async def get_genre(
    id: int,
    db: AsyncSession = Depends(get_session)
):
    
    genre = await search_item_in_db(
        id=id,
        Model=GenreModel,
        session=db
    )

    if not genre:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Gênero não encontrado")
    
    return genre
