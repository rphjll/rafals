"""Miroir exact des tables demande_devis, photo_demande, devis, ligne_devis (db/schema_v13.sql). Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class DemandeDevis(Base):
    __tablename__ = "demande_devis"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    annonce_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("annonce.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    commune_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("commune.id"))
    texte: Mapped[str] = mapped_column(Text)
    adresse_ligne: Mapped[str | None] = mapped_column(Text)
    adresse_complement: Mapped[str | None] = mapped_column(Text)
    code_postal: Mapped[str | None] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(Text, server_default="envoyee")
    motif: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PhotoDemande(Base):
    __tablename__ = "photo_demande"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    demande_devis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("demande_devis.id"))
    fichier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    ordre: Mapped[int] = mapped_column(Integer)


class Devis(Base):
    __tablename__ = "devis"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    demande_devis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("demande_devis.id"))
    blocage_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("blocage.id"))
    annee: Mapped[int] = mapped_column(Integer)
    numero: Mapped[int] = mapped_column(Integer)
    facture_tva: Mapped[bool] = mapped_column(Boolean)
    arrhes_pourcent: Mapped[int] = mapped_column(Integer)
    travaux_debut: Mapped[date] = mapped_column(Date)
    travaux_fin: Mapped[date] = mapped_column(Date)
    valable_jusqu_au: Mapped[date] = mapped_column(Date)
    statut: Mapped[str] = mapped_column(Text, server_default="envoye")
    mode_paiement: Mapped[str | None] = mapped_column(Text)
    envoye_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    accepte_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    termine_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    message: Mapped[str | None] = mapped_column(Text)
    probleme: Mapped[str | None] = mapped_column(Text)
    probleme_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    probleme_traite_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    moyen_direct: Mapped[str | None] = mapped_column(Text)


class LigneDevis(Base):
    __tablename__ = "ligne_devis"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    devis_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("devis.id"))
    ordre: Mapped[int] = mapped_column(Integer)
    libelle: Mapped[str] = mapped_column(Text)
    quantite_centiemes: Mapped[int] = mapped_column(Integer)
    prix_unitaire_centimes: Mapped[int] = mapped_column(Integer)
    tva_pour_mille: Mapped[int | None] = mapped_column(Integer)
