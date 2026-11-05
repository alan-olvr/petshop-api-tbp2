from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Tutor(Base):
    __tablename__ = "tutores"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    telefone: Mapped[str] = mapped_column(String(20))
    email: Mapped[str] = mapped_column(String(120), unique=True)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    animais: Mapped[list["Animal"]] = relationship(back_populates="tutor")
    vinculos: Mapped[list["HistoricoTutela"]] = relationship(back_populates="tutor")