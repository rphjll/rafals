"""Miroir exact des tables categorie_metier, metier, proposition_metier (db/schema_v4.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class CategorieMetier(Base):
    __tablename__ = "categorie_metier"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    code: Mapped[str] = mapped_column(Text)
    nom: Mapped[str] = mapped_column(Text)
    ordre: Mapped[int] = mapped_column(Integer)
    est_active: Mapped[bool] = mapped_column(Boolean, server_default="true")


class Metier(Base):
    __tablename__ = "metier"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    categorie_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("categorie_metier.id"))
    code: Mapped[str] = mapped_column(Text)
    nom: Mapped[str] = mapped_column(Text)
    mots_cles: Mapped[list[str]] = mapped_column(ARRAY(Text), server_default="{}")
    est_active: Mapped[bool] = mapped_column(Boolean, server_default="true")


class PropositionMetier(Base):
    __tablename__ = "proposition_metier"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    propose_par_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    metier_retenu_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("metier.id"))
    decide_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    nom_propose: Mapped[str] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(Text, server_default="en_attente")
    propose_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    decide_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
