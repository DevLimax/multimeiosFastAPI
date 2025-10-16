from typing import List, Optional, Any

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.responses import JSONResponse, Response

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import IntegrityError

from app.models import UserModel, BookModel
from app.models.loanRequest_model import LoanRequestModel, Status as StatusLoanRequest
from app.models.loan_model import LoanModel, Status as StatusLoan
from app.schemas.serializers.loanRequest_serializer import RequestLoanSchemaBase, RequestLoanSchemaUpdate, RequestLoanSchemaCreate

from app.utils.querys_db import search_all_itens_in_db, search_item_in_db
from app.utils.exceptions import NotFoundException, NotPermissionsException, InternalServerException
from app.utils.functions import validate_active_loans_limit

from app.core.deps import get_session, get_current_user

router = APIRouter()

#GET All Requests
@router.get("/", response_model=List[RequestLoanSchemaBase])
async def get_all(db: AsyncSession = Depends(get_session)):
    async with db as session:
        requests = await search_all_itens_in_db(session=session, Model=LoanRequestModel)
        return requests
    
#GET By ID
@router.get("/{id}", response_model=RequestLoanSchemaBase)
async def get(id: int, db: AsyncSession = Depends(get_session)):
    async with db as session:
        request = await search_item_in_db(id=id, session=session, Model=LoanRequestModel)
        if not request:
            NotFoundException(tablename=LoanRequestModel.__tablename__, id=id)

        return request
    
#POST 
@router.post("/", response_model=RequestLoanSchemaBase,status_code=status.HTTP_201_CREATED)
async def post(request: RequestLoanSchemaCreate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):

    validate_active_loans_limit(current_user)
        
    book: BookModel = await search_item_in_db(id=request.book_id, session=db, Model=BookModel)
    if not book or not book.is_active:
        raise NotFoundException(tablename=BookModel.__tablename__, id=request.book_id)
          
    new_request = LoanRequestModel(
        **request.dict(exclude_unset=True)
    ) 
    new_request.user_id = request.user_id if request.user_id else current_user.id
    if current_user.is_admin:
        new_request.changer_by = current_user.id
        

    async with db as session:
        try:
            session.add(new_request)
            await session.commit()
            await session.refresh(new_request)
            return new_request
        except IntegrityError as e:
            await session.rollback()
            print(e)
            raise HTTPException(
                detail=f"Ja existe uma solicitação ativa desse usuario para o livro: {request.book_id}",
                status_code=status.HTTP_409_CONFLICT
            )
        except Exception as e:
            await session.rollback()
            raise InternalServerException()

#PUT 
@router.put("/{id}", response_model=RequestLoanSchemaUpdate, status_code=status.HTTP_202_ACCEPTED)
async def update(id: int, request: RequestLoanSchemaUpdate, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
    if not current_user.is_admin:
        raise NotPermissionsException()
    
    async with db as session:
        request_db = await search_item_in_db(id=id, session=session, Model=LoanRequestModel)
        if not request_db:
            raise NotFoundException(tablename=LoanRequestModel.__tablename__, id=id)
        
        for key, value in request.dict(exclude_unset=True).items():
            if value is not None:
                setattr(request_db, key, value)

        request_db.changer_by = current_user.id

        if request_db.status == StatusLoanRequest.denied_due_lack_stock:
            request_db.is_active = False

        elif request_db.status == StatusLoanRequest.denied_due_user_limit:
            request_db.is_active = False
        
        elif request_db.status == StatusLoanRequest.denied:
            request_db.is_active = False

        await session.commit()
        await session.refresh(request_db)

        if request_db.status == StatusLoanRequest.approved:
            """
                Sempre que uma solicitação for aprovada, vai ser criado o emprestimo automaticamente, com status "Aguardando Retirada".

                Mas o Usuário-Admin (Professor) conseguirá criar um emprestimo manualmente pela API tambem utilizando os Usuários-Aluno e Livros Disponiveis,
                e podendo personalizar tambem as datas de emprestimo e retorno.
            """
            if not request.unique_book_code:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                                    detail="Para aprovar uma solicitação de empréstimo, é necessário informar o código do livro.")
            
            new_bookLoan = LoanModel(
                book_id = request_db.book_id,
                user_id = request_db.user_id,
                unique_book_code_ = int(request.unique_book_code)
            )
            user = await search_item_in_db(id=new_bookLoan.user_id, session=session, Model=UserModel)
            validate_active_loans_limit(user=user)

            book = await search_item_in_db(id=new_bookLoan.book_id, session=session, Model=BookModel)
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
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete(id: int, db: AsyncSession = Depends(get_session), current_user: UserModel = Depends(get_current_user)):
   
    if not current_user.is_admin:
        raise NotPermissionsException()


    async with db as session:
        request = await search_item_in_db(id=id, session=db, Model=LoanRequestModel)
        if not request:
            raise NotFoundException(tablename=LoanRequestModel.__tablename__, id=id)

        try:
            await session.delete(request)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            await session.rollback()
            raise InternalServerException()
            



    


            

        