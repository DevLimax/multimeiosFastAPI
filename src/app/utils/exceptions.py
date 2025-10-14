from fastapi import HTTPException, status

class NotFoundException(HTTPException):
    def __init__(self, id: int):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item {id} não encontrado"
        )

class UniqueViolationException(HTTPException):
    def __init__(self, error: str):
        error_Str = str(error.orig).lower()
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
            detail=f"Já existe um item com ({column} = {value})"
        )