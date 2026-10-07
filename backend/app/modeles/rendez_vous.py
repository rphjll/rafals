"""Miroir exact de la table rendez_vous (db/schema_v9.sql, v10, v15, v23). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class RendezVous(Base):
    __tablename__ = "rendez_vous"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    annonce_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("annonce.id"))  # facultatif depuis schema_v23
    proposition_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("proposition.id"))  # schema_v23
    metier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("metier.id"))  # schema_v23
    commune_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("commune.id"))
    remplace_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("rendez_vous.id"))
    debut: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fin: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    titre: Mapped[str] = mapped_column(Text)
    prix_centimes: Mapped[int | None] = mapped_column(Integer)
    heures: Mapped[int | None] = mapped_column(Integer)
    lieu: Mapped[str] = mapped_column(Text)
    adresse_ligne: Mapped[str | None] = mapped_column(Text)
    adresse_complement: Mapped[str | None] = mapped_column(Text)
    code_postal: Mapped[str | None] = mapped_column(Text)
    mode_paiement: Mapped[str] = mapped_column(Text)
    statut: Mapped[str] = mapped_column(Text)
    motif: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    reponse_avant: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    statut_change_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    rappel_envoye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    absent: Mapped[str | None] = mapped_column(Text)
    absence_signalee_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    contestation: Mapped[str | None] = mapped_column(Text)
    contestee_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    absence_decision: Mapped[str | None] = mapped_column(Text)
    absence_decide_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    absence_decide_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paye_direct_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    paye_direct_moyen: Mapped[str | None] = mapped_column(Text)
