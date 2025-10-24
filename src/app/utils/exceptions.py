from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError

class NotFoundException(HTTPException):
    def __init__(self, id: int, tablename: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Instancia de {tablename} com (id={id}) não encontrada!"
        )

class NotPermissionsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não possui permissões suficientes para essa ação"
        )
        
class NotVerifiedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário nao verificado!"
        )

class UniqueViolationException(HTTPException):
    def __init__(self, error: IntegrityError):
        error_Str = str(error.orig).lower()
        print(error_Str)
        columns = error.statement.split("(",maxsplit=1)[1].split(")")[0].split(",")
        for i, v in enumerate(columns):
            columns[i] = v.strip(" ")
        
        for i, atrr in enumerate(columns):
            if atrr in error_Str:
                print(f"Coluna duplicada: {atrr}")
                column = atrr
                value = error.params[i]
                print("valor:", value)
                break
            
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Já existe uma instancia com ({column} = {value})"
        )
    
class InternalServerException(HTTPException):
    def __init__(self, error):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno do servidor durante operação: {error}"
        )

class UnprocessableEntityException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Servidor não conseguiu processar a requisição"
        )