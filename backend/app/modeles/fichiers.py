"""Miroir exact des tables fichier et accord_parental (db/schema_v3.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Fichier(Base):
    __tablename__ = "fichier"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    depose_par_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    cle_stockage: Mapped[str] = mapped_column(Text)
    nom_origine: Mapped[str] = mapped_column(Text)
    type_mime: Mapped[str] = mapped_column(Text)
    taille_octets: Mapped[int] = mapped_column(BigInteger)
    depose_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class AccordParental(Base):
    __tablename__ = "accord_parental"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    fichier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    decide_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    statut: Mapped[str] = mapped_column(Text, server_default="en_attente")
    depose_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    decide_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    motif_refus: Mapped[str | None] = mapped_column(Text)
