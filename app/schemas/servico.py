from pydantic import BaseModel, ConfigDict, Field
from typing import Optional

class ServicoEntrada(BaseModel):
    nome: str = Field(min_length=2, max_length=120)
    descricao: Optional[str] = Field(default=None, max_length=255)
    valor_padrao: float = Field(gt=0, description="O valor deve ser maior que zero")
    ativo: bool = True

class ServicoSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nome: str
    descricao: Optional[str] 
    valor_padrao: float
    ativo: bool
