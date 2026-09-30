"""Miroir exact des tables commune, prestataire, metier_secondaire (db/schema_v5.sql, v7, v8, v9). Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, Float, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Commune(Base):
    __tablename__ = "commune"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    code_insee: Mapped[str] = mapped_column(Text)
    nom: Mapped[str] = mapped_column(Text)
    codes_postaux: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}")
    departement: Mapped[str] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)


class Prestataire(Base):
    __tablename__ = "prestataire"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    metier_principal_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("metier.id"))
    commune_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("commune.id"))
    photo_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    nom_affiche: Mapped[str] = mapped_column(Text)
    presentation: Mapped[str | None] = mapped_column(Text)
    distance_km: Mapped[int] = mapped_column(Integer)
    siret: Mapped[str | None] = mapped_column(Text)
    siret_statut: Mapped[str] = mapped_column(Text, server_default="absent")
    siret_verifie_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    statut: Mapped[str] = mapped_column(Text, server_default="actif")
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    metier_principal_fin_le: Mapped[date | None] = mapped_column(Date)
    metier_principal_suivant_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("metier.id"))
    agenda_pas_minutes: Mapped[int] = mapped_column(Integer, server_default="15")
    agenda_pause_minutes: Mapped[int] = mapped_column(Integer, server_default="0")
    reservation_delai_min_minutes: Mapped[int] = mapped_column(Integer, server_default="120")
    reservation_delai_max_mois: Mapped[int] = mapped_column(Integer, server_default="2")
    confirmation_automatique: Mapped[bool] = mapped_column(Boolean, server_default="true")
    annulation_delai_heures: Mapped[int] = mapped_column(Integer, server_default="24")


class MetierSecondaire(Base):
    __tablename__ = "metier_secondaire"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    metier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("metier.id"))
    fin_le: Mapped[date | None] = mapped_column(Date)
