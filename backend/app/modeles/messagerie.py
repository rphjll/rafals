"""Miroir exact des tables conversation, message, photo_message (db/schema_v21.sql). Aucun calcul ici."""

from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Identity, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.modeles.base import Base


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    client_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    prestataire_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("prestataire.id"))
    bloquee_par_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("compte.id"))
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    dernier_message_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    client_lu_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    prestataire_lu_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    bloquee_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    conversation_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("conversation.id"))
    auteur_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("compte.id"))
    texte: Mapped[str] = mapped_column(Text)
    genre: Mapped[str] = mapped_column(Text, server_default="texte")
    cree_le: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    mail_envoye_le: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))


class PhotoMessage(Base):
    __tablename__ = "photo_message"

    id: Mapped[int] = mapped_column(BigInteger, Identity(always=True), primary_key=True)
    message_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("message.id"))
    fichier_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("fichier.id"))
    ordre: Mapped[int] = mapped_column(Integer)
