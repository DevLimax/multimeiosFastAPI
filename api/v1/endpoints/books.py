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

from core.deps import get_session, get_current_user

import os
import shutil
import uuid

router = APIRouter()

#GET All Books
@router.get("/", response_model=List[BookSchemaBase], status_code=status.HTTP_200_OK)
async def get_books(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(BookModel)
        result = await session.execute(query)
        books: List[BookModel] = result.scalars().unique().all()
        return books
    
#GET Book by ID
@router.get("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def get_book(book_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(BookModel).filter(BookModel.id == book_id)
        result = await session.execute(query)
        book = result.scalars().unique().one_or_none()

        if not book:
            raise HTTPException(detail="Livro não encontrado", status_code=status.HTTP_404_NOT_FOUND)

        return book
    
#GET Book by ID with Reviews
@router.get("/{book_id}/reviews", response_model=BookSchemaReviews, status_code=status.HTTP_200_OK)
async def get_book_reviews(book_id:int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(BookModel).options(joinedload(BookModel.reviews)).filter(BookModel.id == book_id)
        result = await session.execute(query)
        book = result.scalars().unique().one_or_none()

        if not book:
            raise HTTPException(detail="Livro não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        return book
    
#POST Book
@router.post("/", response_model=BookSchemaBase, status_code=status.HTTP_201_CREATED)
async def create_book(form: BookSchemaForm = Depends(), 
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session), 
                      current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")
    
    filepath = "static/images/covers/bookDefault.png"

    if fileCover:
        if fileCover.content_type not in ["image/jpeg", "image/png"]:
            raise HTTPException(detail="Formato de imagem inválido")
        filename = f"{uuid.uuid4().hex}_{fileCover.filename}"
        filepath = os.path.join("static/images/covers/", filename)
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(fileCover.file, buffer)

    async with db as session:
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
        session.add(new_book)
        await session.commit()
        await session.refresh(new_book)
        return new_book

#PUT Book
@router.put("/{book_id}", response_model=BookSchemaBase, status_code=status.HTTP_200_OK)
async def update_book(book_id: int,
                      book: BookSchemaUpdateForm = Depends(),
                      fileCover: Optional[UploadFile] = File(None),
                      db: AsyncSession = Depends(get_session),
                      current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")
    
    async with db as session:
        query = select(BookModel).filter(BookModel.id == book_id)
        result = await session.execute(query)
        book_up = result.scalars().unique().one_or_none()

        if not book_up:
            raise HTTPException(detail="Livro não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        for key, value in book.__dict__.items():
            if value is not None:
                setattr(book_up, key, value)
        
        if fileCover:
            if fileCover.content_type not in ["image/jpeg", "image/png"]:
                raise HTTPException(detail="Formato de imagem inválido")
            filename = f"{uuid.uuid4().hex}_{fileCover.filename}"
            filepath = os.path.join("static/images/covers/", filename)
            with open(filepath, "wb") as buffer:
                shutil.copyfileobj(fileCover.file, buffer)
            book_up.cover = filepath

        await session.commit()
        await session.refresh(book_up)
        return book_up
    
#DELETE Book
@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
async def del_book(book_id: int, 
                   db: AsyncSession = Depends(get_session),
                   current_user: UserModel = Depends(get_current_user)
):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")

    async with db as session:
        query = select(BookModel).filter(BookModel.id == book_id)
        result = await session.execute(query)
        book = result.scalars().unique().one_or_none()

        if not book:
            raise HTTPException(detail="Livro não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        await session.delete(book)
        await session.commit()
        print(f"Livro {book_id} - {book.title} deletado!")
        return Response(status_code=status.HTTP_204_NO_CONTENT)


