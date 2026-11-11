"""Miroir exact de la table abonnement (db/schema_v31.sql, v32). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Abonnement(Base):
    """Un compte qui suit un prestataire ; muet = plus aucune notification de lui (ex. Julie suit Sophie, muette)."""

    __tablename__ = "abonnement"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    muet: Mapped[bool] = mapped_column(Boolean, server_default="false")  # schema_v32
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
