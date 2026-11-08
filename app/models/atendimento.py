from datetime import datetime
from sqlalchemy import DateTime, ForeignKey, String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Atendimento(Base):
    __tablename__ = "atendimentos"

    id: Mapped[int] = mapped_column(primary_key=True)
    data_hora: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    situacao: Mapped[str] = mapped_column(String(255))
    orientacoes: Mapped[str | None] = mapped_column(Text)

    animal_id: Mapped[int] = mapped_column(ForeignKey("animais.id", ondelete="RESTRICT"), index=True)
    veterinario_id: Mapped[int] = mapped_column(ForeignKey("veterinarios.id", ondelete="RESTRICT"), index=True)
    tutor_id_epoca: Mapped[int] = mapped_column(ForeignKey("tutores.id", ondelete="RESTRICT"))

    servico: Mapped[list["AtendimentoServico"]] = relationship(back_populates="atendimento", cascade="all, delete-orphan")


class AtendimentoServico(Base):
    __tablename__ = "atendimentos_servicos"

    id: Mapped[int] = mapped_column(primary_key=True)
    quantidade: Mapped[int] = mapped_column(default=1)
    valor_cobrado: Mapped[float] = mapped_column(Numeric(10, 2))
 
    atendimento_id: Mapped[int] = mapped_column(ForeignKey("atendimentos.id", ondelete="CASCADE"), index=True)
    servico_id: Mapped[int] = mapped_column(ForeignKey("servicos.id", ondelete="RESTRICT"), index=True)

    atendimento: Mapped["Atendimento"] = relationship(back_populates="servico")