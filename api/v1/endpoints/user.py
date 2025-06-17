from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse, Response
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from schemas.user_schema import UserSchemaBase, UserSchemaCreate, UserSchemaUpdate

from core.deps import get_session, get_current_user
from core.security import generate_hashed_password
from core.auth import create_access_token, authenticate

router = APIRouter()

#GET Logged User
@router.get('/logged', response_model=UserSchemaBase, status_code=status.HTTP_200_OK)
def get_logged(user: UserModel = Depends(get_current_user)):
    return user

#POST Login
@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_session)):
    user = await authenticate(email=form_data.username, password=form_data.password, db=db)

    if not user:
        raise HTTPException(detail="Dados de acesso incorretos!")
    
    return JSONResponse(content={
        "access_token": create_access_token(sub=user.id), 
        "token_type": "bearer"
    },
    status_code=status.HTTP_200_OK)

#POST User
router.post("/singup", response_model=UserSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserSchemaCreate, db: AsyncSession = Depends(get_session)):
    async with db as session:
        new_user = UserModel(
            first_name = user.first_name,
            last_name = user.last_name,
            enrrolment = user.enrrolment,
            email = user.email,
            password = user.password,
            is_admin = user.is_admin,
            profile_image = user.profile_image
        )
        try:
            session.add(new_user)
            await session.commit()
            await session.refresh()
            return new_user
        except IntegrityError:
            raise HTTPException(detail="Já existe um usuário com esse endereço de email", status_code=status.HTTP_409_CONFLICT)
        
#GET All Users
router.get("/", response_model=List[UserSchemaBase])
async def get_users(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UserModel).order_by(UserModel.id)
        result = await session.execute(query)
        users: List[UserModel] = result.scalars().all()
        return users
    
#GET User By ID
router.get("/{user_id}", response_model=UserSchemaBase, status_code=status.HTTP_200_OK)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().unique().one_or_none()

        if not user:
            raise HTTPException(detail="Usúario não encontrado", 
                                status_code=status.HTTP_404_NOT_FOUND)
        return user
    
#PUT User
router.put("/{user_id}", response_model=UserSchemaUpdate, status_code=status.HTTP_202_ACCEPTED)
async def put_user(user_id: int,
                   user: UserSchemaUpdate,
                   db: AsyncSession = Depends(get_session), 
                   current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user_up = result.scalars().unique().one_or_none()

        if not user_up:
            raise HTTPException(detail="Usúario não encontrado", 
                                status_code=status.HTTP_404_NOT_FOUND)
        
        if not current_user.is_admin and user_up.id != current_user.id:
            raise HTTPException(detail="Usuário não tem permissão para alterar outro usuario",status_code=status.HTTP_401_UNAUTHORIZED)
        
        elif current_user.is_admin or user_up.id == current_user.id:
            if user.first_name:
                user_up.first_name == user.first_name
            if user.last_name:
                user_up.last_name == user.last_name
            if user.enrrolment:
                user_up.enrollment == user.enrrolment
            if user.email:
                user_up.email == user.email
            if user.password:
                user_up.password == generate_hashed_password(user.password)
            if user.profile_image:
                user_up.profile_image == user.profile_image
            if user.is_admin:
                user_up.is_admin == user.is_admin
            if user.is_admin == False:
                user_up.is_admin = False
        await session.commit()
        await session.refresh()
        return user_up
    
#DELETE User
router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int ,
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        query = select(UserModel).filter(UserModel.id == user_id)
        result = await session.execute(query)
        user = result.scalars().unique().one_or_none()   
    
    if not user:
        raise HTTPException(detail="Usúario não encontrado", 
            status_code=status.HTTP_404_NOT_FOUND)

    if not current_user.is_admin and user.id != current_user.id:
        raise HTTPException(detail="Usuário não tem permissão para excluir outro usuario",
                            status_code=status.HTTP_401_UNAUTHORIZED)
    
    elif current_user.is_admin or user.id == current_user.id:
        async with db as session:
            await session.delete(user)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        


