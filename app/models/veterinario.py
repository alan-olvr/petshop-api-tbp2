from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base

class Veterinario(Base):
    __tablename__="veterinarios"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    crmv: Mapped[str] = mapped_column(String(20), unique=True)
    especialidade: Mapped[str | None] = mapped_column(String(80))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    