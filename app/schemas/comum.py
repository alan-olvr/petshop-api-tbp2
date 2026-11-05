from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class Pagina(BaseModel, Generic[T]):
    total: int
    offset: int
    limit: int
    itens: list[T]

class Mensagem(BaseModel):
    mensagem: str