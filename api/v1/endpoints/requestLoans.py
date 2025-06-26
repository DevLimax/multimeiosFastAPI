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
from schemas.loanRequest_schema import RequestLoanSchemaBase, RequestLoanSchemaUpdate, RequestLoanSchemaCreate

from utils.search_in_db import *
from utils.exceptionsHttp import not_found, exception_not_identified, unauthorized, user_book_conflict
from utils.functions import validate_active_loans_limit

from core.deps import get_session, get_current_user

router = APIRouter()

#GET All Requests
@router.get("/", response_model=List[RequestLoanSchemaBase])
async def get_all(db: AsyncSession = Depends(get_session)):
    async with db as session:
        requests = await search_all_itens_in_db(db=session, Model=LoanRequestModel)
        return requests
    
#GET By ID
@router.get("/{request_id}", response_model=RequestLoanSchemaBase)
async def get(request_id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        request = await search_item_in_db(id=request_id, db=session, Model=LoanRequestModel)
        if not request:
            not_found()

        return request
    
#POST 
@router.post("/", response_model=RequestLoanSchemaBase,status_code=status.HTTP_201_CREATED)
async def post(request: RequestLoanSchemaCreate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user:
        unauthorized()

    new_request = LoanRequestModel(
       book_id = request.book_id,
       user_id = current_user.id
    ) 

    async with db as session:
        user = await search_item_in_db(id=current_user.id, db=session, Model=UserModel)
        validate_active_loans_limit(user=user)

        try:
            session.add(new_request)
            await session.commit()
            await session.refresh(new_request)
            return new_request
        except IntegrityError:
            await session.rollback()
            user_book_conflict(tablename=LoanRequestModel.__tablename__)

#PUT 
@router.put("/{request_id}", response_model=RequestLoanSchemaUpdate, status_code=status.HTTP_202_ACCEPTED)
async def update(request_id: int, request: RequestLoanSchemaUpdate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        unauthorized()
    
    async with db as session:
        request_db = await search_item_in_db(id=request_id, db=session, Model=LoanRequestModel)
        if not request_db:
            not_found()
        
        for key, value in request.dict(exclude_unset=True).items():
            if value is not None:
                setattr(request_db, key, value)

        request_db.changer_by = current_user.id

        if request_db.status == StatusRequest.denied_due_lack_stock:
            request_db.is_active = False

        elif request_db.status == StatusRequest.denied_due_user_limit:
            request_db.is_active = False
        
        elif request_db.status == StatusRequest.denied:
            request_db.is_active = False

        await session.commit()
        await session.refresh(request_db)

        if request_db.status == StatusRequest.approved:
            """
                Sempre que uma solicitação for aprovada, vai ser criado o emprestimo automaticamente, com status "Aguardando Retirada".

                Mas o Usuário-Admin (Professor) conseguirá criar um emprestimo manualmente pela API tambem utilizando os Usuários-Aluno e Livros Disponiveis,
                e podendo personalizar tambem as datas de emprestimo e retorno.
            """
            if not request.book_code:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                    detail="Para aprovar uma solicitação de empréstimo, é necessário informar o código do livro.")
            
            new_bookLoan = BookLoanModel(
                book_id = request_db.book_id,
                user_id = request_db.user_id,
                book_code = request.book_code
            )
            user = await search_item_in_db(id=new_bookLoan.user_id, db=session, Model=UserModel)
            validate_active_loans_limit(user=user)

            book = await search_item_in_db(id=new_bookLoan.book_id, db=session, Model=BookModel)
            if book.quantity <= 0:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                    detail=f"Esse livro de ID:{book.id} não está disponível para empréstimo. O mesmo se encontra com a quantidade de {book.quantity} unidades.")
            
            try:
                session.add(new_bookLoan)
                book.quantity -= 1
                await session.commit()
                await session.refresh(book)
                await session.refresh(new_bookLoan)
                return Response(content=f"Solicitação aprovada, emprestimo de número ({new_bookLoan.id}) criado.", 
                                status_code=status.HTTP_201_CREATED)
            except Exception as e:
                await session.rollback()
                raise HTTPException(detail=f"Houve um erro na criação do emprestimo após a aprovação: {e}", status_code=status.HTTP_403_FORBIDDEN)
            
        return request_db

#DELETE
@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(request_id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
       unauthorized()
    
    async with db as session:
        request = await search_item_in_db(id=request_id, db=db, Model=LoanRequestModel)
        if not request:
            not_found()

        db.delete(request)
        db.commit()
        return Response(status_code=status.HTTP_204_NO_CONTENT)
            



    


            

        
