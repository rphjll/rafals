"""Miroir exact de la table appareil (db/schema_v28.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Appareil(Base):
    __tablename__ = "appareil"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    adresse: Mapped[str] = mapped_column(Text)
    cle_publique: Mapped[str] = mapped_column(Text)
    cle_secrete: Mapped[str] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    dernier_envoi_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
