from datetime import date

from sqlalchemy import CheckConstraint, Date, ForeignKey, Index, String, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class HistoricoTutela(Base):
    __tablename__="historico_tutela"
    __table_args__= (
        CheckConstraint("motivo IN ('adocao', 'transferencia')", name="motivo_valido"),
        CheckConstraint(
            "data_fim IS NULL OR data_fim >= data_inicio", name="periodo_valido"
        ),

        Index(
            "uq_historico_tutela_vigente",
            "animal_id", 
            unique=True,
            postgresql_where=text("data_fim IS NULL"),
            sqlite_where=text("data_fim IS NULL"),
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    data_inicio: Mapped[date] = mapped_column(Date)
    data_fim: Mapped[date | None] = mapped_column(Date)
    motivo: Mapped[str] = mapped_column(String(20))

    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id", ondelete="RESTRICT"))
    tutor_id: Mapped[int] = mapped_column(ForeignKey("tutores.id", ondelete="RESTRICT"))

    animal: Mapped["Animal"] = relationship(back_populates="historico_tutela")
    tutor: Mapped["Tutor"] = relationship(back_populates="vinculos")