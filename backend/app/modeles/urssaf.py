"""Miroir exact des tables mandat_urssaf et declaration_urssaf (db/schema_v20.sql). Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class MandatUrssaf(Base):
    __tablename__ = "mandat_urssaf"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    numero_secu: Mapped[str | None] = mapped_column(Text)
    texte: Mapped[str] = mapped_column(Text)
    donne_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    retire_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    demonstration: Mapped[bool] = mapped_column(Boolean, server_default="false")


class DeclarationUrssaf(Base):
    __tablename__ = "declaration_urssaf"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    mandat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("mandat_urssaf.id"))
    periodicite: Mapped[str] = mapped_column(Text)
    periode_debut: Mapped[date] = mapped_column(Date)
    nature: Mapped[str] = mapped_column(Text)
    montant_rafals_centimes: Mapped[int] = mapped_column(Integer)
    montant_ailleurs_centimes: Mapped[int] = mapped_column(Integer, server_default="0")
    cotisations_centimes: Mapped[int] = mapped_column(Integer)
    declaree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reference_urssaf: Mapped[str | None] = mapped_column(Text)
    demonstration: Mapped[bool] = mapped_column(Boolean, server_default="false")
