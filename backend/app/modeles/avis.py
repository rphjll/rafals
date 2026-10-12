"""Miroir exact des tables avis et mot_interdit (db/schema_v11.sql), avis_client (db/schema_v27.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Avis(Base):
    __tablename__ = "avis"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    rendez_vous_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rendez_vous.id"))
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    cache_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    note: Mapped[int] = mapped_column(Integer)
    texte: Mapped[str] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modifie_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    retire_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reponse: Mapped[str | None] = mapped_column(Text)
    repondu_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signale_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signalement: Mapped[str | None] = mapped_column(Text)
    signalement_traite_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cache_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cache_motif: Mapped[str | None] = mapped_column(Text)


class AvisClient(Base):
    """L'avis du prestataire sur le client : mêmes rubriques que Avis, dans l'autre sens."""

    __tablename__ = "avis_client"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    rendez_vous_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rendez_vous.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    cache_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    note: Mapped[int] = mapped_column(Integer)
    texte: Mapped[str] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modifie_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    retire_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    reponse: Mapped[str | None] = mapped_column(Text)
    repondu_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signale_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    signalement: Mapped[str | None] = mapped_column(Text)
    signalement_traite_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cache_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cache_motif: Mapped[str | None] = mapped_column(Text)


class MotInterdit(Base):
    __tablename__ = "mot_interdit"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    ajoute_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    mot: Mapped[str] = mapped_column(Text)
    ajoute_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
