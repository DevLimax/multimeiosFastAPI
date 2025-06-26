from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.user_model import UserModel
from models.book_model import BookModel
from schemas.book_schema import BookSchemaBase, BookSchemaReviews, BookSchemaUpdateForm, BookSchemaForm

from utils.search_in_db import *
from utils.exceptionsHttp import not_found, exception_not_identified, unauthorized

from core.deps import get_session, get_current_user

import os
import shutil
import uuid

router = APIRouter()

#GET All Books
@router.get("/", response_model=List[BookSchemaBase], status_code=status.HTTP_200_OK)
async def get_books(db: AsyncSession = Depends(get_session)):
    async with db as session:
        books = await search_all_itens_in_db(db=session, Model=BookModel)
        try:
            return books
        except Exception as e:
            raise exception_not_identified(e)
        
#GET Book by ID
@router.get("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        book = await search_item_in_db(id=book_id, db=session, Model=BookModel)
        if not book:
            not_found()

        return book
    
#GET Book by ID with Reviews
@router.get("/{book_id}/reviews", response_model=BookSchemaReviews, status_code=status.HTTP_200_OK)
async def get_book_reviews(book_id:int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        book = await search_item_in_db(id=book_id, db=session, Model=BookModel)
        if not book:
            not_found()

        return book
    
#POST Book
@router.post("/", response_model=BookSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_book(form: BookSchemaForm = Depends(), 
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session), 
                      current_user: UserModel = Depends(get_current_user)
):
    """
        Recebe um formulário com os dados do livro e uma imagem de capa opcional.
        Se a imagem for fornecida, deve ser do tipo JPEG ou PNG.
        Se não for fornecida, será usada uma imagem padrão.
        Retorna a instancia do livro criado ou um erro 409-Conflict se já existir um livro com o mesmo titulo e autor, ou so titulo.
        
        Campos:
        - title: Titulo de livro (obrigatório, dever ser único). 
        - author: Autor do livro (obrigatório, um autor tem varios livros, mas um livro tem apenas um autor).
        - synopsis: Sinopse do livro (opcional).
        - genre_id: Id do gênero existente na tabela Genres (obrigatório)
        - genre_two_id: Id do gênero existente na tabela Genres (opcional)
        - quantity: Quantidade de exemplares disponiveis (obrigatório)
        - cover: Imagem de capa do livro (opcional - retorna uma imagem default caso seja null).
        - added_by: Id do usuario (Professor-Admin) que adicionou o livro. (preenchido automaticamente pelo current_user)
        
        Exceptions:
        - HTTPException 409-Conflict: (Se não existir gênero com id fornecido) - (Se existir um livro com mesmo titulo e autor na base de dados ou somente o mesmo titulo).
        - HTTPException 400-Bad Request: Se a imagem de capa for fornecida e nao for do tipo JPEG ou PNG.
        - HTTP 422 Unprocessable Entity: Se o formulário for inválido.
        - HTTP 500 Internal Server Error: Se houver algum erro interno no servidor.
    """
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")

    if fileCover:
        if fileCover.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
        filename = f"{uuid.uuid4().hex}_{fileCover.filename}"
        filepath = os.path.join("static/images/covers/", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(fileCover.file, buffer)
    else:
        filepath = "static/images/covers/bookDefault.png"

    new_book = BookModel(
        title=form.title,
        author=form.author,
        synopsis=form.synopsis,
        genre_id=form.genre,
        genre_two_id=form.genre_two,
        quantity=form.quantity,
        cover=filepath,
        added_by=current_user.id
    )

    try:
        db.add(new_book)
        await db.commit()
        await db.refresh(new_book)
        return new_book
    
    except IntegrityError as e:
        error_str = str(e).lower()
        if "(title, author)" in error_str:
            await db.rollback()
            raise HTTPException(detail="Já existe uma instancia na tabela (Livros) com o mesmo Titulo e Autor", status_code=status.HTTP_409_CONFLICT)
        
        elif "(title)" in error_str:    
            await db.rollback()
            raise HTTPException(detail="Já existe uma instancia na tabela (Livros) com o mesmo Titulo", status_code=status.HTTP_409_CONFLICT)
        
        elif "(genre_id)" in error_str:
            await db.rollback()
            raise HTTPException(detail=f"Gênero ({form.genre}) não existe", status_code=status.HTTP_409_CONFLICT)
        
        elif "(genre_two_id)" in error_str:
            await db.rollback()
            raise HTTPException(detail=f"Gênero ({form.genre_two}) não existe", status_code=status.HTTP_409_CONFLICT)
        
    except Exception as e:
        await db.rollback()
        raise exception_not_identified(e)

#PUT Book
@router.put("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def update_book(book_id: int,
                      book: BookSchemaUpdateForm = Depends(),
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        unauthorized()
        
    async with db as session:
        book_db = await search_item_in_db(id=book_id, db=session, Model=BookModel)

        if not book_db:
            not_found()
        
        for key, value in book.__dict__.items():
            if value is not None:
                setattr(book_db, key, value)
        
        if fileCover:
            if fileCover.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido")
            filename = f"{uuid.uuid4().hex}_{fileCover.filename}"
            filepath = os.path.join("static/images/covers/", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(fileCover.file, buffer)
            book_db.cover = filepath

        await session.commit()
        await session.refresh(book_db)
        return book_db
    
#DELETE Book
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_book(book_id: int, 
                   db: AsyncSession = Depends(get_session),
                   current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        unauthorized()

    async with db as session:
        book = await search_item_in_db(id=book_id, db=session, Model=BookModel)

        if not book:
            not_found()
        
        await session.delete(book)
        await session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)


