from sqlalchemy.orm import DeclarativeMeta
from models.user_model import UserModel
from models.bookloan_model import BookLoanModel, Status as StatusLoan
from fastapi import HTTPException, status, UploadFile
from typing import Type
import os
import shutil
import uuid

def validate_active_loans_limit(user: UserModel):
    """
        Retorna um HTTPException caso o usuario tenha excedido o limite de emprestimos ativos.
        Retorna para o algoritimo normal caso usuario não tenha excedido o limite de emprestimos ativos.
    """
    if not user:
        raise HTTPException(detail="Usuário nao encontrado!", status_code=status.HTTP_404_NOT_FOUND)
    active_loans: int = 0
    for loan in user.loans:
        if loan.status == StatusLoan.awaiting_return and loan.is_active or loan.status == StatusLoan.not_returned and loan.is_active:
            active_loans += 1
    if active_loans >= 2:
        raise HTTPException(detail="Usuário Excedeu o limite de Emprestimos!", status_code=status.HTTP_400_BAD_REQUEST)
    return  

async def expands_loans_requests_reviews(model: Type[DeclarativeMeta], expand: list[str]) -> dict:
    """
    Retorna um dicionario com as informacoes dos emprestimos, solicitações de emprestimos e avaliações caso o modelo possua essas relações.
    """
    model_dict = model.__dict__
    if not expand:
        model_dict.pop('loans')
        model_dict.pop('reviews')
        model_dict.pop('requestLoans')
        return model_dict
    if not "loans" in expand:
        model_dict['loans'] = None
    if not "reviews" in expand:
        model_dict['reviews'] = None
    if not "requestLoans" in expand:
        model_dict['requestLoans'] = None
    return model_dict
        
async def upload_image(image: UploadFile, folder: str) -> str:
    """
    Recebe uma arquivo e o nome da pasta que deve ser enviada.
    
    se a função validar a imagem como formato indesejado, será lançado um hTTPException.
    senão, a imagem será salva na pasta indicada e o caminho dela será retornado para salvar no banco.
    """
    if image.content_type not in ["image/jpeg", "image/png"]:
        raise HTTPException(detail="Formato de imagem inválido", status_code=status.HTTP_400_BAD_REQUEST)
    filename = f"{uuid.uuid4().hex}_{image.filename}"
    filepath = os.path.join("static/images/profiles/", filename)
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)
        return filepath
