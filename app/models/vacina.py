from datetime import date
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Date,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    text,
    true,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Vacina(Base):
    __tablename__ = "vacinas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    fabricante: Mapped[str] = mapped_column(String(120))
    dias_reforco: Mapped[int] = mapped_column(Integer)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default=true())

class AplicacaoVacina(Base):
    __tablename__ = "aplicacoes_vacinas"
    __table_args__ = (
        CheckConstraint("status IN ('prevista', 'aplicada')", name = "status_valido"),
        UniqueConstraint(
            "animal_id", "vacina_id", "dose",
            name="uq_aplicacoes_vacinas_animal_vacina_dose",
        ),
    )
    id: Mapped[int] = mapped_column(primary_key=True)
    dose: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))
    data_prevista: Mapped[date] = mapped_column(Date)
    data_aplicacao: Mapped[date | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20))

    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id", ondelete="RESTRICT"), index=True)
    vacina_id: Mapped[int] = mapped_column(ForeignKey("vacinas.id", ondelete="RESTRICT"), index=True)
    veterinario_id: Mapped[int | None] = mapped_column(ForeignKey("veterinarios.id", ondelete="RESTRICT"))