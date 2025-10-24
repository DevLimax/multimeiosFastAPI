from typing import List, Optional, Any, Annotated

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError, DBAPIError

from app.models.user_model import UserModel
from app.models.loan_model import Status
from app.schemas.serializers.user_serializer import UserSchemaBase, UserSchemaWithExtras, UserSchemaCreateForm, UserSchemaUpdateForm
from app.schemas.filters.user_filters import UserFilter

from app.core.deps import get_session, get_current_user
from app.core.security import generate_hashed_password

from app.utils.querys_db import search_item_in_db, search_all_itens_in_db
from app.utils.exceptions import UniqueViolationException, NotFoundException, InternalServerException, NotPermissionsException, UnprocessableEntityException
from app.Emails.send_email import send_email_verification_code

from datetime import datetime
import os
import shutil
import uuid

router = APIRouter()

#Metodo POST para criar um usuário
@router.post( "/", 
            response_model=UserSchemaBase, 
            status_code=status.HTTP_201_CREATED
)
async def create_user(
                form: UserSchemaCreateForm = Depends(),
                profileImage: Optional[UploadFile] = File(None),
                db: AsyncSession = Depends(get_session)
) -> JSONResponse:  
    
    if profileImage:
        try:
            
            if profileImage.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
            
            filename = f"{uuid.uuid4().hex}_{profileImage.filename}"
            filepath = os.path.join("static/images/profiles/", filename)
            
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(profileImage.file, buffer)
                
        except Exception as e:
            raise HTTPException(detail=f"Erro ao salvar imagem - Details: {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)  
    else:
        filepath = "static/images/profiles/defaultProfile.png"

    new_user = UserModel(first_name = form.first_name,
                        last_name = form.last_name,
                        enrollment = form.enrollment,
                        email = form.email,
                        password = generate_hashed_password(form.password),
                        is_admin = form.is_admin,
                        profile_image = filepath)
    
    await new_user.generate_verification_code() #Gera o codigo de verificação
    
    try:
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        send_email_verification_code(receiver_email=new_user.email, 
                                     code=new_user.verification_code, 
                                     username=new_user.first_name)# -> Envia o email de verificação contendo o codigo gerado pela função acima!
        return new_user
    
    except IntegrityError as e:
        """
        Exceções do banco de dados geralmente caem no IntegrityError nesse endpoint o mais comum seria o de UniqueViolation,
        pois o email precisa ser unico e o username também, por isso o tratamento de erro foi feito dessa maneira.
        """
        await db.rollback()
        if "uniqueviolation" in str(e.orig).lower():
            raise UniqueViolationException(error=e)
        else:
            raise HTTPException(detail=f"Erro de integridade: {e.orig}", status_code=status.HTTP_409_CONFLICT)
    
    except Exception as e:
        await db.rollback()
        raise HTTPException(detail=f"Erro interno do servidor: {e}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#Metodo GET para buscar todos os usuários - suporte a FILTROS
@router.get("/", 
            response_model=List[UserSchemaBase]
)
async def get_users(
    db: AsyncSession = Depends(get_session),
    filters: UserFilter = Depends(UserFilter)
) -> List[UserSchemaBase]:
    
    async with db as session:
        users = await search_all_itens_in_db(Model=UserModel, 
                                            session=session,
                                            filters=filters)
        
        try:
            return users
        except Exception as e:
            raise InternalServerException(error=e)
    
#Metodo GET para buscar um usuário
@router.get("/{id}", 
            response_model=UserSchemaWithExtras, 
            status_code=status.HTTP_200_OK
)
async def get_user(id: int, 
                   db: AsyncSession = Depends(get_session)
) -> UserSchemaWithExtras:
        
    async with db as session:
        try:
            user = await search_item_in_db(id=id, 
                                        session=session, 
                                        Model=UserModel)
        except Exception as e:
            raise UnprocessableEntityException()
        
        if not user:
            raise NotFoundException(id=id, 
                                    tablename=UserModel.__tablename__)                  
        return user
  
    
#Metodo PUT para atualizar dados de um usuário
@router.put("/{id}", 
            response_model=UserSchemaBase, 
            status_code=status.HTTP_202_ACCEPTED
)
async def put_user(id: int,
                   data: UserSchemaUpdateForm = Depends(),
                   profileImage: Optional[UploadFile] = File(None),
                   db: AsyncSession = Depends(get_session), 
                   current_user: UserModel = Depends(get_current_user)
) -> UserSchemaBase:
    
    async with db as session:
        user_db: UserModel = await search_item_in_db(id=id, 
                                          session=session, 
                                          Model=UserModel)
        
        if not user_db:
            raise NotFoundException(id)
        
        if not current_user.is_admin and id != current_user.id:
            raise NotPermissionsException()
        
        for key, value in data.__dict__.items():
            if value is not None:
                
                if key == "password": #-> Caso seja alterado a senha, esse if cuida de gerar um hash para a nova senha
                    value = generate_hashed_password(value)
                    
                setattr(user_db, key, value)
        
        if profileImage:
            if profileImage.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
            filename = f"{uuid.uuid4().hex}_{profileImage.filename}"
            filepath = os.path.join("static/images/profiles/", filename)
            with open("src/app/"+filepath, "wb") as buffer:
                shutil.copyfileobj(profileImage.file, buffer)
            user_db.profile_image = filepath
            
        try:
            await session.commit()
            await session.refresh(user_db)
            return user_db
        except IntegrityError as e:
            await session.rollback()
            e_str = str(e.orig).lower()
            if "uniqueviolation" in str(e.orig).lower():
                if "email" in e_str:
                    raise HTTPException(detail=f"Já existe uma instancia com (email = {data.email})", status_code=status.HTTP_409_CONFLICT)
                else:
                    raise HTTPException(detail=f"Já existe uma instancia com (enrollment = {data.enrollment})", status_code=status.HTTP_409_CONFLICT)
            else:
                raise HTTPException(detail=f"Erro de integridade {e.orig}", status_code=status.HTTP_409_CONFLICT)
    
        except Exception as e:
            await session.rollback()
            print(e)
            raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#DELETE User
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(id: int ,
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    async with db as session:
        user = await search_item_in_db(id=id, session=session, Model=UserModel)
        if not user:
            raise NotFoundException(id=id)

        if not current_user.is_admin and user.id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acesso negado")
        
        elif current_user.is_admin or user.id == current_user.id:
            try:
                await session.delete(user)
                await session.commit()
                return Response(status_code=status.HTTP_204_NO_CONTENT)
            except Exception as e:
                await session.rollback()
                raise HTTPException(detail="Erro interno do servidor", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    