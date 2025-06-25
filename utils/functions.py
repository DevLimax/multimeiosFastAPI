from models.user_model import UserModel
from models.bookloan_model import BookLoanModel, Status as StatusLoan
from fastapi import HTTPException, status

def validate_active_loans_limit(user: UserModel):
    """
        Retorna um HTTPException caso o usuario tenha excedido o limite de emprestimos ativos.
        Retorna para o algoritimo normal caso usuario não tenha excedido o limite de emprestimos ativos.
    """
    active_loans: int = 0

    for loan in user.loans:
        if loan.status == StatusLoan.awaiting_return and loan.is_active or loan.status == StatusLoan.not_returned and loan.is_active:
            active_loans += 1

    if active_loans >= 2:
        raise HTTPException(detail="Usuário Excedeu o limite de Emprestimos!", status_code=status.HTTP_400_BAD_REQUEST)
    
    return  
