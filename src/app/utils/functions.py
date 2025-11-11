from app.models.user_model import UserModel
from app.models.loan_model import LoanModel, Status as StatusLoan
from fastapi import HTTPException, status

def validate_active_loans_limit(user: UserModel):
    """
        Retorna um HTTPException caso o usuario tenha excedido o limite de emprestimos ativos.
        Retorna para o algoritimo normal caso usuario não tenha excedido o limite de emprestimos ativos.
    """
    if not user:
        raise HTTPException(detail="Usuário nao encontrado!", status_code=status.HTTP_404_NOT_FOUND)
    
    active_loans: int = 0

    for loan in user.loans:
        if loan.status not in [StatusLoan.canceled, 
                               StatusLoan.lost, 
                               StatusLoan.returned, 
                               StatusLoan.returned_after_the_deadlin] and loan.is_active:
            
            active_loans += 1

    if active_loans > 2:
        raise HTTPException(detail="Usuário Excedeu o limite de Emprestimos!", status_code=status.HTTP_400_BAD_REQUEST)
    
    return  

def user_expands(user: UserModel, expand: list[str]) -> dict:
    """
    Função recebe o usuário e as expansões desejadas (user: UserModel, expand -> [loans, reviews, requestLoans]) -> Retorna um dicionário mesclando os dados ja existentes com as expansões desejadas
    
    caso não seja requisitado alguma expansão o dicionário será retornado sem essas expansões, 
    retornando -> {loans: None, reviews: None, requestLoans: None}.
    """
    user_dict = user.__dict__
    if not expand:
        user_dict.pop('loans')
        user_dict.pop('reviews')
        user_dict.pop('requestLoans')
        return user_dict
    
    if not "loans" in expand:
        user_dict['loans'] = None
    
    if not "reviews" in expand:
        user_dict['reviews'] = None
    
    if not "requestLoans" in expand:
        user_dict['requestLoans'] = None
        
    return user_dict
        
    