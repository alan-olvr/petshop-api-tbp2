from datetime import date
from typing import Optional, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class VacinaEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    fabricante: str = Field(min_length=2, max_length=120)
    dias_reforco: int = Field(ge=0)
    ativo: bool = True

class VacinaAtualizacao(BaseModel):
    nome: Optional[str] = Field(default=None, min_length=2, max_length=120)
    fabricante: Optional[str] = Field(default=None, max_length=120)
    dias_reforco: Optional[int] = Field(default=None, ge=0)
    ativo: Optional[bool] = None

    @model_validator(mode="after")
    def nao_permitir_nulos(self):
        if any(v is None for v in self.model_dump(exclude_unset=True).values()):
            raise ValueError("Não envie campos nulos")
        return self

class VacinaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    nome: str
    fabricante: str
    dias_reforco: int
    ativo: bool

class AplicacaoVacinaEntrada(BaseModel):
    data_prevista: date
    status: Literal["prevista", "aplicada"] = "prevista"
    animal_id: int
    vacina_id: int
    veterinario_id: Optional[int] = None
    dose: int = Field(ge=1, default=1)
    data_aplicacao: Optional[date] = None
    @model_validator(mode="after")
    def validar_status_e_data(self):
        if self.status == "aplicada" and self.data_aplicacao is None:
            raise ValueError("A data de aplicação deve ser fornecida quando o status for 'aplicada'.")
        if self.status == "prevista" and self.data_aplicacao is not None:
            raise ValueError("A data de aplicação não deve ser fornecida quando o status for 'prevista'.")
        return self


class AplicacaoVacinaAtualizacao(BaseModel):
    dose: Optional[int] = Field(default=None, ge=1)
    data_prevista: Optional[date] = None
    data_aplicacao: Optional[date] = None
    status: Optional[Literal["prevista", "aplicada"]] = None
    veterinario_id: Optional[int] = None

    @model_validator(mode="after")
    def nao_permitir_nulos_obrigatorios(self):
        enviados = self.model_dump(exclude_unset=True)
        for campo in ("dose", "data_prevista", "status"):
            if campo in enviados and enviados[campo] is None:
                raise ValueError(f"O campo '{campo}' não aceita nulo")
        return self

class AplicacaoVacinaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    dose: int
    data_prevista: date
    data_aplicacao: Optional[date]
    status: Literal["prevista", "aplicada"]
    animal_id: int
    vacina_id: int
    veterinario_id: Optional[int]
