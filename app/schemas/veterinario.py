from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints, model_validator
from app.schemas.tutor import Texto

Crmv = Annotated[str, StringConstraints(strip_whitespace=True, to_upper=True, min_length=4, max_length=20)]

class VeterinarioEntrada(BaseModel):
    nome: Texto
    crmv: Crmv
    especialidade: Texto | None = None
    ativo: bool = True

class VeterinarioAtualizacao(BaseModel):
    nome: Texto | None = None
    crmv: Crmv | None = None
    especialidade: Texto | None = None
    ativo: bool | None = None

    @model_validator(mode="after")
    def nao_permitir_nulos(self):
        if any(v is None for v in self.model_dump(exclude_unset=True).values()):
            raise ValueError("Não envie campos nulos")
        return self

class VeterinarioSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    crmv: str
    especialidade: str | None
    ativo: bool