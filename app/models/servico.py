from sqlalchemy import Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.models.base import Base


class Servico(Base):
    __tablename__ = "servicos"
    id: Mapped[int] = mapped_column(primary_key=True)
    nome: Mapped[str] = mapped_column(String(120), index=True, unique=True)
    valor_padrao: Mapped[float] = mapped_column(Numeric(10, 2))
    ativo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="1")
    