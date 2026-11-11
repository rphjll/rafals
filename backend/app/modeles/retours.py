"""Miroir exact de la table retour (db/schema_v34.sql, lot 13.1). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Retour(Base):
    """Un message « Un problème ? Une idée ? » (ex. Julie : probleme, « Le bouton Publier ne répond pas »)."""

    __tablename__ = "retour"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    auteur_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    fichier_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("fichier.id", ondelete="SET NULL"))
    sorte: Mapped[str] = mapped_column(Text)
    texte: Mapped[str] = mapped_column(Text)
    page: Mapped[str] = mapped_column(Text)
    appareil: Mapped[str] = mapped_column(Text)
    navigateur: Mapped[str] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(Text, server_default="a_traiter")
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
