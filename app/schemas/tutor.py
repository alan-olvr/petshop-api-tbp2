from typing import Annotated

from pydantic import (
    BaseModel, 
    ConfigDict,
    EmailStr,
    Field,
    StringConstraints,
    model_validator,
)

Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=120)]
Telefone = Annotated[str, StringConstraints(strip_whitespace=True, min_length=8, max_length=20)]

class TutorEntrada(BaseModel):
    nome: Texto
    telefone: Telefone
    email: EmailStr
    ativo: bool = True

class TutorAtualizacao(BaseModel):
    nome: Texto
    telefone: Telefone
    email: EmailStr | None = None
    ativo: bool = True

    @model_validator(mode="after")
    def nao_permitir_nulos(self):
        if any(v is None for v in self.model_dump(exclude_unset=True).values()):
            raise ValueError("Não envie campos nulos")
        return self

class TutorSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    telefone: str
    email: str 
    ativo: bool