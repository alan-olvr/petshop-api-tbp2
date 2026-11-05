from datetime import date
from typing import Annotated, Literal

from pydantic import AfterValidator, BaseModel, ConfigDict, model_validator

from app.schemas.tutor import Texto

def _nao_futura(valor: date) -> date:
    if valor > date.today():
        raise ValueError("A data de nascimento não pode estar no futuro")
    return valor 

DataNascimento = Annotated[date, AfterValidator(_nao_futura)]
Sexo = Literal["M", "F"]

class AnimalEntrada(BaseModel):
    nome: Texto
    especie: Texto
    raca: Texto | None = None
    sexo: Sexo
    data_nasc_aprox: DataNascimento | None = None
    ativo: bool = True
    tutor_id: int

class AnimalAtualizacao(BaseModel):
    model_config = ConfigDict(extra="forbid")

    nome: Texto | None = None
    especie: Texto | None = None  
    raca: Texto | None = None
    sexo: Sexo | None = None
    data_nasc_aprox: DataNascimento | None = None
    ativo: bool | None = None

    @model_validator(mode="after")
    def nao_permitir_nulos(self):
        if any(v is None for v in self.model_dump(exclude_unset=True).values()):
            raise ValueError("Não envie campos nulos")
        return self

class TutorResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str

class MicrochipResumo(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    numero: str

class AnimalSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    especie: str
    raca: str
    sexo: str
    data_nasc_aprox: date | None
    ativo: bool
    tutor_id: int
    tutor: TutorResumo
    microchip: MicrochipResumo | None = None    