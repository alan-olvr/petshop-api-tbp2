from datetime import date

from sqlalchemy import Date, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

class Microchip(Base):
    __tablename__= "microchips"

    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(15), unique=True)
    data_implantacao: Mapped[date | None] = mapped_column(Date)

    animal_id: Mapped[int] = mapped_column(
        ForeignKey("animais.id", ondelete="CASCADE"), unique=True
    )

    animal: Mapped["Animal"] = relationship(back_populates="microchip")
