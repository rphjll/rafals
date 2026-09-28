"""Envoi des mails. Sur le PC, ils arrivent dans Mailpit (http://localhost:8025)."""

import smtplib
from email.message import EmailMessage

from app import config


def envoyer_mail(destinataire: str, sujet: str, texte: str) -> None:
    message = EmailMessage()
    message["From"] = config.MAIL_EXPEDITEUR
    message["To"] = destinataire
    message["Subject"] = sujet
    message.set_content(texte)
    with smtplib.SMTP(config.SMTP_HOTE, config.SMTP_PORT, timeout=10) as serveur:
        serveur.send_message(message)
