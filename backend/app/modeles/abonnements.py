"""Miroir exact de la table abonnement (db/schema_v31.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Abonnement(Base):
    """Un compte qui suit un prestataire, avec les notifications choisies pour lui (ex. Julie suit Karim)."""

    __tablename__ = "abonnement"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    notif_creneau: Mapped[bool] = mapped_column(Boolean, server_default="true")
    notif_nouveaute: Mapped[bool] = mapped_column(Boolean, server_default="true")
    notif_retour: Mapped[bool] = mapped_column(Boolean, server_default="true")
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
