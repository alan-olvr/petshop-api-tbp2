from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class AtendimentoServicoEntrada(BaseModel):
    servico_id: int
    quantidade: int = Field(gt=0, default=1)
    valor_cobrado: float = Field(gt=0)

class AtendimentoServicoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    servico_id: int
    quantidade: int
    valor_cobrado: float

class AtendimentoEntrada(BaseModel):
    situacao: str = Field(min_length=3, max_length=255)
    orientacao: Optional[str] = Field(default=None, max_length=500)
    animal_id: int
    veterinario_id: int
    tutor_id_epoca: int
    servicos: list[AtendimentoServicoEntrada] = Field(min_length=1)

class AtendimentoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    data_hora: datetime
    situacao: str
    orientacoes: Optional[str]
    animal_id: int
    veterinario_id: int
    tutor_id_epoca: int
    servicos: list[AtendimentoServicoSaida]
    