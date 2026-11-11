"""« Un problème ? Une idée ? » (RM-RETOURS.md, lot 13.1) : seulement connecté, problème ou idée, 10 à 2 000 caractères,
une capture JPG ou PNG facultative, 5 messages par jour, page / appareil / navigateur ajoutés tout seuls,
message injurieux gardé (statut « injurieux ») au lieu d'être refusé."""

from datetime import UTC, datetime

from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modeles.fichiers import Fichier
from app.modeles.retours import Retour
from app.services.retours import appareil_et_navigateur, envoyes_aujourd_hui

CHROME_ANDROID = ("Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/130.0.0.0 Mobile Safari/537.36")
FIREFOX_WINDOWS = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:132.0) Gecko/20100101 Firefox/132.0"
PNG = b"\x89PNG\r\n\x1a\n zztest capture"


def envoyer(compte, sorte="probleme", texte="Le bouton Publier ne répond pas", page="/demandes/nouvelle",
            capture=None, navigateur=CHROME_ANDROID):
    fichiers = {"capture": capture} if capture else None
    return compte.client.post("/api/retours", data={"sorte": sorte, "texte": texte, "page": page}, files=fichiers,
                              headers={"User-Agent": navigateur})


def test_julie_signale_un_probleme_avec_une_capture(fabrique_compte, base: Session) -> None:
    julie = fabrique_compte()
    reponse = envoyer(julie, capture=("ecran.png", PNG, "image/png"))
    assert reponse.status_code == 201, reponse.text
    assert reponse.json()["message"] == "Merci, c'est envoyé. Nous regardons chaque soir."
    retour = base.get_one(Retour, reponse.json()["id"])
    assert (retour.auteur_id, retour.sorte, retour.texte, retour.page, retour.statut) == (
        julie.id, "probleme", "Le bouton Publier ne répond pas", "/demandes/nouvelle", "a_traiter")
    assert (retour.appareil, retour.navigateur) == ("telephone", "Chrome sur Android")
    assert base.get_one(Fichier, retour.fichier_id).type_mime == "image/png"


def test_karim_propose_une_idee_sans_capture(fabrique_compte, base: Session) -> None:
    karim = fabrique_compte()
    reponse = envoyer(karim, sorte="idee", texte="Pouvoir mettre une vidéo de mon travail", page="/profil",
                      navigateur=FIREFOX_WINDOWS)
    assert reponse.status_code == 201, reponse.text
    retour = base.get_one(Retour, reponse.json()["id"])
    assert (retour.sorte, retour.fichier_id, retour.appareil, retour.navigateur) == (
        "idee", None, "ordinateur", "Firefox sur Windows")


def test_il_faut_etre_connecte(client: TestClient) -> None:
    reponse = client.post("/api/retours", data={"sorte": "probleme", "texte": "Le bouton ne répond pas"})
    assert reponse.status_code == 401


def test_refus_sorte_inconnue_texte_trop_court_ou_trop_long(fabrique_compte) -> None:
    julie = fabrique_compte()
    assert "Choisissez « Un problème » ou « Une idée »" in envoyer(julie, sorte="autre").json()["detail"]
    assert envoyer(julie, texte="bug").json()["detail"] == "Décrivez un peu plus (10 caractères au moins)."
    assert "2000 caractères au plus" in envoyer(julie, texte="a" * 2001).json()["detail"]
    assert envoyer(julie, texte="   abc     ").status_code == 400  # 3 caractères une fois les espaces retirés


def test_capture_pdf_ou_trop_lourde_refusee(fabrique_compte, base: Session) -> None:
    julie = fabrique_compte()
    pdf = envoyer(julie, capture=("ecran.pdf", b"%PDF-1.4 zztest", "application/pdf"))
    assert pdf.status_code == 400 and "envoyez un JPG, PNG" in pdf.json()["detail"]
    lourde = envoyer(julie, capture=("ecran.png", PNG + b"0" * (5 * 1024 * 1024), "image/png"))
    assert lourde.status_code == 400 and "trop lourd" in lourde.json()["detail"]
    assert base.scalar(select(Retour.id).where(Retour.auteur_id == julie.id)) is None  # rien d'enregistré


def test_cinq_messages_par_jour(fabrique_compte, base: Session) -> None:
    julie = fabrique_compte()
    for n in range(5):
        assert envoyer(julie, texte=f"Problème numéro {n + 1} sur la page").status_code == 201
    sixieme = envoyer(julie, texte="Problème numéro 6 sur la page")
    assert sixieme.status_code == 429
    assert sixieme.json()["detail"] == ("Vous avez déjà envoyé 5 messages aujourd'hui, merci ! "
                                        "Vous pourrez en envoyer d'autres demain.")
    # Un autre compte n'est pas gêné
    assert envoyer(fabrique_compte()).status_code == 201


def test_le_compteur_repart_a_minuit_heure_de_paris(fabrique_compte, base: Session) -> None:
    julie = fabrique_compte()
    from app.modeles.comptes import Compte

    compte = base.get_one(Compte, julie.id)
    # 23 h 50 à Paris le 09/11 (22 h 50 UTC), puis 0 h 10 à Paris le 10/11 (23 h 10 UTC le 09/11)
    base.add(Retour(auteur_id=julie.id, sorte="idee", texte="zztest message de la veille", page="/", appareil="ordinateur",
                    navigateur="Firefox sur Windows", statut="a_traiter", cree_le=datetime(2026, 11, 9, 22, 50, tzinfo=UTC)))
    base.commit()
    assert envoyes_aujourd_hui(base, compte, datetime(2026, 11, 9, 22, 55, tzinfo=UTC)) == 1
    assert envoyes_aujourd_hui(base, compte, datetime(2026, 11, 9, 23, 10, tzinfo=UTC)) == 0


def test_message_injurieux_garde_pour_l_administrateur(fabrique_compte, base: Session, ia_de_moderation) -> None:
    julie = fabrique_compte()
    # L'IA (simulée) trouve ce texte injurieux : il n'est pas refusé, il est mis de côté
    reponse = envoyer(julie, texte="ZZINJURE votre site est nul")
    assert reponse.status_code == 201
    assert base.get_one(Retour, reponse.json()["id"]).statut == "injurieux"
    # IA en panne : le message passe avec la seule liste des mots interdits
    ia_de_moderation["panne"] = 1
    assert base.get_one(Retour, envoyer(julie, texte="ZZINJURE encore une fois").json()["id"]).statut == "a_traiter"


def test_appareil_et_navigateur_lus_dans_le_user_agent() -> None:
    iphone = ("Mozilla/5.0 (iPhone; CPU iPhone OS 18_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) "
              "Version/18.0 Mobile/15E148 Safari/604.1")
    edge = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 "
            "Safari/537.36 Edg/130.0.0.0")
    assert appareil_et_navigateur(iphone) == ("telephone", "Safari sur iPhone")
    assert appareil_et_navigateur(edge) == ("ordinateur", "Edge sur Windows")
    assert appareil_et_navigateur("") == ("ordinateur", "Navigateur inconnu")
