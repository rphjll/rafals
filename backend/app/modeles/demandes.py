"""Miroir exact des tables demande, photo_demande_publiee (db/schema_v22.sql). Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Date, DateTime, Float, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Demande(Base):
    __tablename__ = "demande"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    metier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("metier.id"))
    commune_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("commune.id"))
    cachee_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    titre: Mapped[str] = mapped_column(Text)
    description: Mapped[str] = mapped_column(Text)
    quand: Mapped[str] = mapped_column(Text)
    jour: Mapped[date | None] = mapped_column(Date)
    lieu: Mapped[str] = mapped_column(Text, server_default="chez_moi")
    budget_centimes: Mapped[int | None] = mapped_column(Integer)
    adresse_ligne: Mapped[str | None] = mapped_column(Text)
    adresse_complement: Mapped[str | None] = mapped_column(Text)
    code_postal: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    statut: Mapped[str] = mapped_column(Text, server_default="ouverte")
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expire_le: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    rappel_envoye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cachee_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cachee_motif: Mapped[str | None] = mapped_column(Text)


class PhotoDemandePubliee(Base):
    __tablename__ = "photo_demande_publiee"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    demande_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("demande.id"))
    fichier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    ordre: Mapped[int] = mapped_column(Integer)
