from fastapi import HTTPException, status

def exception_not_identified(error: Exception) -> HTTPException:
    raise HTTPException(detail=f"Não foi possivel identificar o erro:{error}", status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

def not_found(variable: str):
    raise HTTPException(detail=f"{variable} não encontrado".capitalize(), status_code=status.HTTP_404_NOT_FOUND)

def unauthorized():
    """
        Reutilização de codigo para usar nas validações de permissão do Usuário
    """
    raise HTTPException(detail="Usuario com permissões insuficientes para realizar essa ação!", status_code=status.HTTP_401_UNAUTHORIZED)

def unauthenticated():
    raise HTTPException(detail="Usuário não autenticado!", status_code=status.HTTP_401_UNAUTHORIZED)

def user_book_conflict(tablename: str):
    """
        Esse Exception irá servir como uma reutilização de codigo para capturar o IntegrityError causado pelo conflito de instancias com o mesmo User_id e Book_id,
        que pode ser nas tabelas: Emprestimos, Solicitações de emprestimos, Avaliacoes. todas requerem um Usuário e Livro
    """
    raise HTTPException(detail=f"Já existe uma instancia na tabela ({tablename.title()}) com o mesmo Usuário e Livro!", status_code=status.HTTP_409_CONFLICT)
