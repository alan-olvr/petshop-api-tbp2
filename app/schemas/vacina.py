from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class VacinaEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    fabricante: Optional[str] = Field(default=None, max_length=120)
    dias_reforco: Optional[int] = Field(default=None, ge=0)
    ativo: bool = True

class VacinaAtualizacao(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    fabricante: Optional[str] = Field(default=None, max_length=120)
    dias_reforco: Optional[int] = Field(default=None, ge=0)
    ativo: Optional[bool] = None

class VacinaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    fabricante: Optional[str]
    dias_reforco: Optional[int]
    ativo: bool

class AplicacaoVacinaEntrada(BaseModel):
    data_prevista: date
    status: Literal["Prevista", "Aplicada"] = "Prevista"
    animal_id: int
    vacina_id: int
    veterinario_id: Optional[int] = None
    dose: int = Field(ge=1, default=1)
    data_aplicacao: Optional[date] = None
    @model_validator(mode="after")
    def validar_status_e_data(self):
        if self.status == "Aplicada" and self.data_aplicacao is None:
            raise ValueError("A data de aplicação deve ser fornecida quando o status for 'Aplicada'.")
        if self.status == "Prevista" and self.data_aplicacao is not None:
            raise ValueError("A data de aplicação não deve ser fornecida quando o status for 'Prevista'.")
        return self


class AplicacaoVacinaAtualizacao(BaseModel):
    dose: Optional[int] = Field(default=None, ge=1)
    data_prevista: Optional[date] = None
    data_aplicacao: Optional[date] = None
    status: Optional[Literal["Prevista", "Aplicada"]] = None
    veterinario_id: Optional[int] = None

class AplicacaoVacinaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dose: int
    data_prevista: date
    data_aplicacao: Optional[date]
    status: Literal["Prevista", "Aplicada"]
    animal_id: int
    vacina_id: int
    veterinario_id: Optional[int]
