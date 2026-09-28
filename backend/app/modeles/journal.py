"""Miroir exact de la table journal_action (db/schema_v3.sql). Aucun calcul ici."""

from datetime import datetime
from typing import Any

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Text, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class JournalAction(Base):
    __tablename__ = "journal_action"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    auteur_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    action: Mapped[str] = mapped_column(Text)
    table_cible: Mapped[str] = mapped_column(Text)
    ligne_id: Mapped[int | None] = mapped_column(BigInteger)
    avant: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    apres: Mapped[dict[str, Any] | None] = mapped_column(JSONB)
    fait_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
