from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from models.loanRequest_model import LoanRequestModel, Status as StatusRequest
from models.user_model import UserModel
from models.book_model import BookLoanModel, BookModel
from models.bookloan_model import Status as StatusLoan
from schemas.loanRequest_schema import LoanSchemaBase, LoanSchemaUpdate

from core.deps import get_session, get_current_user

router = APIRouter()

#GET All Requests
@router.get("/", response_model=List[LoanSchemaBase])
async def get_all(db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(LoanRequestModel).order_by(LoanRequestModel.id)
        result = await session.execute(query)
        requests = result.scalars().unique().all()
        return requests
    
#GET By ID
@router.get("/{request_id}", response_model=LoanSchemaBase)
async def get(request_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        query = select(LoanRequestModel).filter(LoanRequestModel.id == request_id)
        result = await session.execute(query)
        request = result.scalars().unique().one_or_none()

        if not request:
            raise HTTPException(detail="Solicitação de empestimo não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        return request
    
#POST 
@router.post("/", response_model=LoanSchemaBase,status_code=status.HTTP_201_CREATED)
async def post(request: LoanSchemaBase, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    async with db as session:
        new_request = LoanRequestModel(
           book_id = request.book_id,
           user_id = current_user.id
        ) 
        try:
            session.add(new_request)
            await session.commit()
            await session.refresh(new_request)
            return new_request
        except IntegrityError:
            await session.rollback()
            raise HTTPException(detail="Já existe uma solicitação desse usuário para o livro!", status_code=status.HTTP_409_CONFLICT)

#PUT 
@router.put("/{request_id}", response_model=LoanSchemaUpdate, status_code=status.HTTP_202_ACCEPTED)
async def update(request_id: int, request: LoanSchemaUpdate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")
    
    async with db as session:
        query = select(LoanRequestModel).filter(LoanRequestModel.id == request_id)
        result = await session.execute(query)
        request_db = result.scalars().unique().one_or_none()

        if not request_db:
            raise HTTPException(detail="Solicitação de empestimo não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        for key, value in request.dict(exclude_unset=True).items():
            if value is not None:
                setattr(request_db, key, value)
        request_db.changer_by = current_user.id
        await session.commit()
        await session.refresh(request_db)

        if request_db.status == StatusRequest.approved:
            new_bookLoan = BookLoanModel(
                book_id = request_db.book_id,
                user_id = request_db.user_id,
                status = StatusLoan.awaiting_withdrawal
            )
            try:
                session.add(new_bookLoan)
                result = await session.execute(select(BookModel).filter(BookModel.id == new_bookLoan.book_id))
                book = result.scalars().unique().one_or_none()
                book.quantity -= 1
                await session.commit()
                await session.refresh(book)
                await session.refresh(new_bookLoan)
                return Response(content=f"Solicitação aprovada, emprestimo de número ({new_bookLoan.id}) criado e aguardando a retirada do livro.", 
                                status_code=status.HTTP_202_ACCEPTED)
            except Exception as e:
                await session.rollback()
                raise HTTPException(detail=f"Houve um erro na criação do emprestimo: error {e}", status_code=status.HTTP_403_FORBIDDEN)

        return request_db

#DELETE
@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(request_id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuario não autorizado")
    
    async with db as session:
        query = select(LoanRequestModel).filter(LoanRequestModel.id == request_id)
        result = await session.execute(query)
        request = result.scalars().unique().one_or_none()

        if not request:
            raise HTTPException(detail="Solicitação de empestimo não encontrado", status_code=status.HTTP_404_NOT_FOUND)
        
        session.delete(request)
        session.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
            



    


            

        
