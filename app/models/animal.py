from datetime import date

from sqlalchemy import Boolean, CheckConstraint, Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Animal(Base):
    __tablename__="animais"
    __table_args__= (
        CheckConstraint("sexo IN ('M', 'F')", name="sexo_valido"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True)
    especie: Mapped[str] = mapped_column(String(60), index=True)
    raca: Mapped[str] = mapped_column(String(60))
    sexo: Mapped[str] = mapped_column(String(1))
    data_nasc_aprox: Mapped[date | None] = mapped_column(Date)
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")

    tutor_id: Mapped[int] = mapped_column(
        ForeignKey("tutores.id", ondelete="RESTRICT"), index=True
    )

    tutor: Mapped["Tutor"] = relationship(back_populates="animais")

    microchip: Mapped["Microchip | None"] = relationship(
        back_populates="animal", uselist=False, cascade="all, delete-orphan"
    )

    historico_tutela: Mapped[list["HistoricoTutela"]] = relationship(
        back_populates="animal", order_by="HistoricoTutela.data_inicio"
    )