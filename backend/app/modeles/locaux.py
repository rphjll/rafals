"""Miroir exact de la table local (db/schema_v7.sql ; ses voisines annonce et photo_annonce ont été supprimées par
db/schema_v29.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Local(Base):
    __tablename__ = "local"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    commune_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("commune.id"))
    ligne: Mapped[str] = mapped_column(Text)
    complement: Mapped[str | None] = mapped_column(Text)
    code_postal: Mapped[str] = mapped_column(Text)
    modifie_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
