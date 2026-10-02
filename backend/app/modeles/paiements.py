"""Miroir exact de la table paiement (db/schema_v12.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Paiement(Base):
    __tablename__ = "paiement"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    rendez_vous_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("rendez_vous.id"))
    montant_centimes: Mapped[int] = mapped_column(Integer)
    commission_centimes: Mapped[int] = mapped_column(Integer)
    statut: Mapped[str] = mapped_column(Text, server_default="a_payer")
    stripe_paiement: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    paye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    frais_stripe_centimes: Mapped[int | None] = mapped_column(Integer)
    verse_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    stripe_versement: Mapped[str | None] = mapped_column(Text)
    rembourse_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    rembourse_centimes: Mapped[int | None] = mapped_column(Integer)
    stripe_remboursement: Mapped[str | None] = mapped_column(Text)
