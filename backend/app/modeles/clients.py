"""Miroir exact de la table adresse (db/schema_v6.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Adresse(Base):
    __tablename__ = "adresse"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    commune_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("commune.id"))
    ligne: Mapped[str] = mapped_column(Text)
    complement: Mapped[str | None] = mapped_column(Text)
    code_postal: Mapped[str] = mapped_column(Text)
    modifiee_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
