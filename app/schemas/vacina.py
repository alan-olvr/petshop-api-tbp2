from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field

class VacinaEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    fabricante: Optional[str] = Field(default=None, max_length=120)
    dias_reforco: Optional[int] = Field(default=None, ge=0)
    ativo: bool = True

class VacinaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    fabricante: Optional[str]
    dias_reforco: Optional[int]
    ativo: bool

class AplicacaoVacinaEntrada(BaseModel):
    data_prevista: date
    status: Literal["Prevista", "Aplicada"] = "prevista"
    animal_id: int
    vacina_id: int
    veterinario_id: Optional[int] = None