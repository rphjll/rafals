"""Miroir exact des tables facture et ligne_facture (db/schema_v15.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Facture(Base):
    __tablename__ = "facture"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    client_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    rendez_vous_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("rendez_vous.id"))
    devis_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("devis.id"))
    paiement_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("paiement.id"))
    avoir_de_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("facture.id"))
    sorte: Mapped[str] = mapped_column(Text)
    annee: Mapped[int] = mapped_column(Integer)
    numero: Mapped[int] = mapped_column(Integer)
    emise_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    objet: Mapped[str] = mapped_column(Text)
    moyen_paiement: Mapped[str | None] = mapped_column(Text)
    vendeur_nom: Mapped[str] = mapped_column(Text)
    vendeur_siret: Mapped[str] = mapped_column(Text)
    vendeur_adresse: Mapped[str] = mapped_column(Text)
    acheteur_nom: Mapped[str] = mapped_column(Text)
    acheteur_adresse: Mapped[str | None] = mapped_column(Text)
    mention_tva: Mapped[str | None] = mapped_column(Text)


class LigneFacture(Base):
    __tablename__ = "ligne_facture"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    facture_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("facture.id"))
    ordre: Mapped[int] = mapped_column(Integer)
    libelle: Mapped[str] = mapped_column(Text)
    quantite_centiemes: Mapped[int] = mapped_column(Integer)
    prix_unitaire_centimes: Mapped[int] = mapped_column(Integer)
    tva_pour_mille: Mapped[int | None] = mapped_column(Integer)
