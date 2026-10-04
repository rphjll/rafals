"""Miroir exact des tables dossier_creation et piece_dossier (db/schema_v18.sql, complété par schema_v19.sql).
Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class DossierCreation(Base):
    __tablename__ = "dossier_creation"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    metier_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("metier.id"))
    commune_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("commune.id"))
    naissance_commune_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("commune.id"))
    civilite: Mapped[str | None] = mapped_column(Text)
    nom_naissance: Mapped[str | None] = mapped_column(Text)
    nom_usage: Mapped[str | None] = mapped_column(Text)
    prenoms: Mapped[str | None] = mapped_column(Text)
    naissance_le: Mapped[date | None] = mapped_column(Date)
    naissance_pays: Mapped[str | None] = mapped_column(Text)
    nationalite: Mapped[str | None] = mapped_column(Text)
    situation_famille: Mapped[str | None] = mapped_column(Text)
    numero_secu: Mapped[str | None] = mapped_column(Text)
    adresse_rue: Mapped[str | None] = mapped_column(Text)
    mail: Mapped[str | None] = mapped_column(Text)
    telephone: Mapped[str | None] = mapped_column(Text)
    pere_nom: Mapped[str | None] = mapped_column(Text)
    mere_nom: Mapped[str | None] = mapped_column(Text)
    description: Mapped[str | None] = mapped_column(Text)
    debut_le: Mapped[date | None] = mapped_column(Date)
    lieu_travail: Mapped[str | None] = mapped_column(Text)
    local_adresse: Mapped[str | None] = mapped_column(Text)
    nom_commercial: Mapped[str | None] = mapped_column(Text)
    activite_en_meme_temps: Mapped[str | None] = mapped_column(Text)
    ancien_siren: Mapped[str | None] = mapped_column(Text)
    periodicite: Mapped[str | None] = mapped_column(Text)
    impot_avec_cotisations: Mapped[bool | None] = mapped_column(Boolean)
    acre_demandee: Mapped[bool | None] = mapped_column(Boolean)
    adresse_non_publique: Mapped[bool | None] = mapped_column(Boolean)
    statut: Mapped[str] = mapped_column(Text, server_default="brouillon")
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    modifie_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    certifie_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pouvoir_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    pouvoir_texte: Mapped[str | None] = mapped_column(Text)
    envoye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    guichet_id: Mapped[str | None] = mapped_column(Text)
    guichet_numero: Mapped[str | None] = mapped_column(Text)
    motif: Mapped[str | None] = mapped_column(Text)
    corriger_avant_le: Mapped[date | None] = mapped_column(Date)
    siret_recu: Mapped[str | None] = mapped_column(Text)
    sensible_efface_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    # schema_v19 : le code postal de l'adresse, et la ville du local
    code_postal: Mapped[str | None] = mapped_column(Text)
    local_commune_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("commune.id"))
    local_code_postal: Mapped[str | None] = mapped_column(Text)


class PieceDossier(Base):
    __tablename__ = "piece_dossier"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    dossier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("dossier_creation.id"))
    fichier_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    sorte: Mapped[str] = mapped_column(Text)
    depose_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    a_refaire: Mapped[bool] = mapped_column(Boolean, server_default="false")
    efface_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
