from datetime import date
from typing import Literal
from pydantic import BaseModel, ConfigDict, computed_field, field_validator
from app.schemas.animal import TutorResumo

MotivoTutela = Literal["adocao", "transferencia"]

class TransferenciaTutela(BaseModel):
    novo_tutor_id: int
    motivo: MotivoTutela = "transferencia"
    data_transferencia: date | None = None

    @field_validator("data_transferencia")
    @classmethod
    def nao_futura(cls, valor: date | None):
        if valor is not None and valor > date.today():
            raise ValueError("A data da transferência não pode estar no futuro")
        return valor

class TutelaSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int
    tutor_id: int
    tutor: TutorResumo
    data_inicio: date
    data_fim: date | None
    motivo: str

    @computed_field
    @property
    def vigente(self) -> bool:
        return self.data_fim is None