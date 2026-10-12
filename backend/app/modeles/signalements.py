"""Miroir exact des tables signalement et rappel_declaration (db/schema_v17.sql). Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Signalement(Base):
    __tablename__ = "signalement"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    auteur_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    prestataire_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("prestataire.id"))  # facultatif depuis schema_v21
    annonce_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("annonce.id"))
    conversation_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("conversation.id"))  # schema_v21
    demande_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("demande.id"))  # schema_v27
    traite_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    motif: Mapped[str] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    statut: Mapped[str] = mapped_column(Text, server_default="a_traiter")
    decision: Mapped[str | None] = mapped_column(Text)
    traite_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class RappelDeclaration(Base):
    __tablename__ = "rappel_declaration"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    periode_debut: Mapped[date] = mapped_column(Date)
    sorte: Mapped[str] = mapped_column(Text)
    envoye_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
