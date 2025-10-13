from fastapi import APIRouter, HTTPException, Depends, Query, status
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user_model import UserModel, UserSchemaBase, UserSchemaCreate, UserSchemaUpdate
from app.core.deps import get_session
from app.utils.querys_db import search_item_in_db, search_all_itens_in_db

#Bypass warning SQLModel Select
from sqlmodel.sql.expression import Select, SelectOfScalar

SelectOfScalar.inherit_cache = True
Select.inherit_cache = True
#Bypass end

router = APIRouter()

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=UserSchemaBase)
async def create_user(
    user: UserSchemaCreate, 
    db:AsyncSession = Depends(get_session)
) -> UserModel:
    
    new_user = UserModel(**user.dict())
    
    try:
        new_user.validate_date()
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@router.get("/", response_model=List[UserSchemaBase], status_code=status.HTTP_200_OK)
async def get_users(
    db: AsyncSession = Depends(get_session),
    first_name: Optional[str] = Query(default=None, description="Filtro pelo primeiro nome do Usuário")
):
    users: Optional[List[UserModel]] = await search_all_itens_in_db(
        Model=UserModel, 
        session=db
    )
    return users

@router.get("/{id}", response_model=UserSchemaBase, status_code=status.HTTP_200_OK)
async def get_user(
    id: int,
    db: AsyncSession = Depends(get_session),
):
    user: Optional[UserModel] = await search_item_in_db(
        id=id,
        Model=UserModel,
        session=db
    )
    
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário nao encontrado")
    
    return user