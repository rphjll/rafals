"""Envoi des mails. Sur le PC, ils arrivent dans Mailpit (http://localhost:8025) ; en ligne, ils partiront par Brevo
(.doc/technique/HEBERGEMENT.md § « Envoi des mails en ligne »)."""

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
        # Un vrai service d'envoi (Brevo) demande de se connecter, sur une liaison chiffrée ; Mailpit, non
        if config.SMTP_UTILISATEUR:
            serveur.starttls()
            serveur.login(config.SMTP_UTILISATEUR, config.SMTP_MOT_DE_PASSE)
        serveur.send_message(message)
