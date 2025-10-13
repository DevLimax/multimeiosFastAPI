from typing import Optional, List
from pydantic import EmailStr

from sqlmodel import Field, SQLModel, ForeignKey, Relationship, Enum as EnumSQL

from app.models.base_model import BaseModel
from app.core.security import generate_hashed_password

from enum import Enum

class TypeChoices(str, Enum):
    PROFESSOR = "professor"
    ALUNO = "aluno"

class UserModel(BaseModel, table=True):
    __tablename__ = "usuarios"
    
    id: Optional[int] = Field(primary_key=True, index=True)
    first_name: str = Field(nullable=False, max_length=100)
    last_name: str = Field(nullable=False, max_length=100)
    type: TypeChoices = Field(nullable=False, default=TypeChoices.ALUNO)
    enrollment: int = Field(nullable=True, unique=True, max_digits=9)
    email: EmailStr = Field(nullable=False, max_length=144, unique=True)
    password: str = Field(nullable=False, max_length=50)
    is_admin: bool = Field(default=False)
    
    books_added: List["BookModel"] = Relationship(back_populates="added_by")
    
    def validate_date(self):
        if isinstance(self.id, int) and self.id < 1:
            raise ValueError("ID invalido!")
        
        if self.enrollment < 1:
            raise ValueError("Matricula invalida!")
        
        if self.first_name and self.last_name:
            self.first_name = self.first_name.title()
            self.last_name = self.last_name.title()
            
        if self.password:
            self.password = generate_hashed_password(self.password)
            
            
class UserSchemaBase(SQLModel, table=False):
    id: Optional[int] = None
    first_name: str
    last_name: str
    type: TypeChoices
    enrollment: int
    email: EmailStr
    is_admin: bool
    
class UserSchemaCreate(UserSchemaBase):
    password: str
    
class UserSchemaUpdate(UserSchemaCreate):
    first_name: Optional[str]
    last_name: Optional[str]
    type: Optional[TypeChoices]
    enrollment: Optional[int]
    email: Optional[EmailStr]
    password: Optional[str]
    is_admin: Optional[bool]
    