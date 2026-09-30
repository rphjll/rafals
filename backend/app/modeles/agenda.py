"""Miroir exact des tables plage_horaire et blocage (db/schema_v8.sql). Aucun calcul ici."""

from datetime import datetime, time

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, Text, Time, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class PlageHoraire(Base):
    __tablename__ = "plage_horaire"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    jour_semaine: Mapped[int] = mapped_column(Integer)
    debut: Mapped[time] = mapped_column(Time)
    fin: Mapped[time] = mapped_column(Time)


class Blocage(Base):
    __tablename__ = "blocage"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    debut: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fin: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    motif: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
