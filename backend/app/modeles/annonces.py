"""Miroir exact des tables local, annonce, photo_annonce (db/schema_v7.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, Integer, Text, func
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


class Annonce(Base):
    __tablename__ = "annonce"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    metier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("metier.id"))
    titre: Mapped[str] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    forme_prix: Mapped[str] = mapped_column(Text)
    prix_centimes: Mapped[int | None] = mapped_column(Integer)
    duree_minutes: Mapped[int | None] = mapped_column(Integer)
    heures_min: Mapped[int | None] = mapped_column(Integer)
    heures_max: Mapped[int | None] = mapped_column(Integer)
    lieu: Mapped[str] = mapped_column(Text)
    paiement_carte: Mapped[bool] = mapped_column(Boolean, server_default="false")
    paiement_especes: Mapped[bool] = mapped_column(Boolean, server_default="true")
    statut: Mapped[str] = mapped_column(Text, server_default="en_ligne")
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modifiee_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PhotoAnnonce(Base):
    __tablename__ = "photo_annonce"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    annonce_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("annonce.id"))
    fichier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    ordre: Mapped[int] = mapped_column(Integer)
