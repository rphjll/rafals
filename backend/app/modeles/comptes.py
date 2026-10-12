"""Miroir exact des tables compte, session, jeton_mail (db/schema_v2.sql, v3, v6). Aucun calcul ici."""

from datetime import date, datetime

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Compte(Base):
    __tablename__ = "compte"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    email: Mapped[str] = mapped_column(Text)
    mot_de_passe_hache: Mapped[str] = mapped_column(Text)
    prenom: Mapped[str] = mapped_column(Text)
    nom: Mapped[str] = mapped_column(Text)
    telephone: Mapped[str | None] = mapped_column(Text)  # facultatif dans la base depuis schema_v6 (effacé à la fermeture)
    date_naissance: Mapped[date | None] = mapped_column(Date)  # idem
    email_verifie_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    echecs_connexion: Mapped[int] = mapped_column(Integer, server_default="0")
    bloque_jusqu_au: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    derniere_connexion_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    est_administrateur: Mapped[bool] = mapped_column(Boolean, server_default="false")  # schema_v3
    ferme_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # schema_v6
    avis_recus_vus_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # schema_v27
    inactivite_prevenue_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))  # schema_v6


class SessionConnexion(Base):
    """Table « session » (nommée ainsi en Python pour ne pas se confondre avec la session SQLAlchemy)."""

    __tablename__ = "session"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    jeton_hache: Mapped[str] = mapped_column(Text)
    appareil: Mapped[str | None] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expire_le: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    fermee_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class JetonMail(Base):
    __tablename__ = "jeton_mail"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    compte_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    usage: Mapped[str] = mapped_column(Text)
    jeton_hache: Mapped[str] = mapped_column(Text)
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    expire_le: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    utilise_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
