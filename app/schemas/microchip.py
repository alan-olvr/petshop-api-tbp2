from datetime import date
from typing import Annotated
from pydantic import BaseModel, ConfigDict, StringConstraints, field_validator

NumeroMicrochip = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^\d{15}$")]

class MicrochipEntrada(BaseModel):
    numero: NumeroMicrochip  # padrão ISO: 15 dígitos
    data_implantacao: date | None = None

    @field_validator("data_implantacao")
    @classmethod
    def nao_futura(cls, valor: date | None):
        if valor is not None and valor > date.today():
            raise ValueError("A data de implantação não pode estar no futuro")
        return valor

class MicrochipSaida(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: str
    data_implantacao: date | None
    animal_id: int

