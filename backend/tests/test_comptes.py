"""Un test par règle de .doc/regles-metier/RM-COMPTES.md (lot 1.1)."""

from datetime import UTC, date, datetime, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.conftest import MOT_DE_PASSE_TEST, email_essai, jeton_du_mail


def reponse_inscription(client: TestClient, email: str, **modifs: object):
    donnees = {
        "email": email,
        "mot_de_passe": MOT_DE_PASSE_TEST,
        "prenom": "Marie",
        "nom": "ZZTEST Dupont",
        "telephone": "06 12 34 56 78",
        "date_naissance": "1972-03-12",
        **modifs,
    }
    return client.post("/api/comptes", json=donnees)


def connexion(client: TestClient, email: str, mot_de_passe: str = MOT_DE_PASSE_TEST):
    return client.post("/api/connexion", json={"email": email, "mot_de_passe": mot_de_passe})


# ---------- Inscription ----------


def test_inscription_envoie_un_lien_de_verification(client, mails_envoyes) -> None:
    email = email_essai()
    reponse = reponse_inscription(client, email)

    assert reponse.status_code == 201
    assert reponse.json()["email_verifie"] is False
    assert len(mails_envoyes) == 1
    assert mails_envoyes[0]["a"] == email
    assert "/verifier-adresse?jeton=" in mails_envoyes[0]["texte"]


def test_adresse_enregistree_en_minuscules(client, mails_envoyes) -> None:
    email = email_essai()
    reponse = reponse_inscription(client, "  " + email.upper() + " ")

    assert reponse.json()["email"] == email


def test_une_adresse_ne_sert_qu_une_fois(client, mails_envoyes) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    reponse = reponse_inscription(client, email)

    assert reponse.status_code == 409
    assert reponse.json()["detail"] == "Un compte existe déjà avec cette adresse mail."


def test_mot_de_passe_trop_court_refuse(client, mails_envoyes) -> None:
    # RM-COMPTES : « soleil » est refusé, « MaisonBleue44 » est accepté
    refuse = reponse_inscription(client, email_essai(), mot_de_passe="soleil")
    accepte = reponse_inscription(client, email_essai(), mot_de_passe="MaisonBleue44")

    assert refuse.status_code == 400
    assert "au moins 10 caractères" in refuse.json()["detail"]
    assert accepte.status_code == 201


def test_moins_de_16_ans_refuse(client, mails_envoyes) -> None:
    aujourd_hui = datetime.now(UTC).date()
    quinze_ans = date(aujourd_hui.year - 15, aujourd_hui.month, 1)
    seize_ans_pile = aujourd_hui.replace(year=aujourd_hui.year - 16)

    refuse = reponse_inscription(client, email_essai(), date_naissance=quinze_ans.isoformat())
    accepte = reponse_inscription(client, email_essai(), date_naissance=seize_ans_pile.isoformat())

    assert refuse.status_code == 400
    assert "au moins 16 ans" in refuse.json()["detail"]
    assert accepte.status_code == 201


# ---------- Vérification de l'adresse ----------


def test_le_lien_verifie_l_adresse_une_seule_fois(client, mails_envoyes) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    jeton = jeton_du_mail(mails_envoyes[0])

    premier = client.post("/api/comptes/verification", json={"jeton": jeton})
    second = client.post("/api/comptes/verification", json={"jeton": jeton})
    connexion(client, email)

    assert premier.status_code == 200
    assert client.get("/api/moi").json()["email_verifie"] is True
    assert second.status_code == 400
    assert second.json()["detail"] == "Ce lien a déjà été utilisé. Demandez-en un nouveau."


def test_lien_de_verification_expire(client, mails_envoyes, base: Session) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    jeton = jeton_du_mail(mails_envoyes[0])
    base.execute(
        text("UPDATE jeton_mail SET expire_le = now() - interval '1 minute' "
             "WHERE compte_id = (SELECT id FROM compte WHERE email = :e)"),
        {"e": email},
    )
    base.commit()

    reponse = client.post("/api/comptes/verification", json={"jeton": jeton})

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Ce lien a expiré. Demandez-en un nouveau."


# ---------- Connexion et blocage ----------


def test_connexion_puis_deconnexion(client, mails_envoyes) -> None:
    email = email_essai()
    reponse_inscription(client, email)

    reponse = connexion(client, email)
    assert reponse.status_code == 200
    assert client.get("/api/moi").json()["email"] == email

    client.post("/api/deconnexion")
    assert client.get("/api/moi").status_code == 401


def test_mauvais_mot_de_passe_meme_message_qu_adresse_inconnue(client, mails_envoyes) -> None:
    email = email_essai()
    reponse_inscription(client, email)

    mauvais = connexion(client, email, "MotDePasseFaux1")
    inconnu = connexion(client, email_essai())

    assert mauvais.status_code == inconnu.status_code == 401
    assert mauvais.json()["detail"] == inconnu.json()["detail"] == "Adresse mail ou mot de passe incorrect."


def test_cinq_erreurs_bloquent_15_minutes(client, mails_envoyes, base: Session) -> None:
    email = email_essai()
    reponse_inscription(client, email)

    for _ in range(4):
        assert connexion(client, email, "MotDePasseFaux1").status_code == 401
    cinquieme = connexion(client, email, "MotDePasseFaux1")
    bon_mot_de_passe_pendant_blocage = connexion(client, email)

    assert cinquieme.status_code == 423
    assert "connexion bloquée jusqu'à" in cinquieme.json()["detail"]
    assert bon_mot_de_passe_pendant_blocage.status_code == 423
    assert "réessayez après" in bon_mot_de_passe_pendant_blocage.json()["detail"]

    # 15 minutes plus tard (on avance le temps en reculant la fin du blocage)
    base.execute(
        text("UPDATE compte SET bloque_jusqu_au = now() - interval '1 second' WHERE email = :e"), {"e": email}
    )
    base.commit()
    assert connexion(client, email).status_code == 200


def test_une_connexion_reussie_remet_le_compteur_a_zero(client, mails_envoyes, base: Session) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    for _ in range(4):
        connexion(client, email, "MotDePasseFaux1")

    connexion(client, email)

    echecs = base.execute(text("SELECT echecs_connexion FROM compte WHERE email = :e"), {"e": email}).scalar_one()
    assert echecs == 0


def test_session_expiree_apres_30_jours(client, mails_envoyes, base: Session) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    connexion(client, email)
    assert client.get("/api/moi").status_code == 200

    expire = base.execute(
        text("SELECT expire_le - cree_le FROM session WHERE compte_id = (SELECT id FROM compte WHERE email = :e)"),
        {"e": email},
    ).scalar_one()
    base.execute(
        text("UPDATE session SET expire_le = now() - interval '1 second' "
             "WHERE compte_id = (SELECT id FROM compte WHERE email = :e)"),
        {"e": email},
    )
    base.commit()

    assert expire == timedelta(days=30)
    assert client.get("/api/moi").status_code == 401


# ---------- Mot de passe oublié ----------


def test_mot_de_passe_oublie_adresse_inconnue_meme_reponse_sans_mail(client, mails_envoyes) -> None:
    reponse = client.post("/api/mot-de-passe/oubli", json={"email": email_essai()})

    assert reponse.status_code == 200
    assert mails_envoyes == []


def test_mot_de_passe_oublie_change_le_mot_de_passe(client, mails_envoyes) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    connexion(client, email)
    client.post("/api/mot-de-passe/oubli", json={"email": email})
    jeton = jeton_du_mail(mails_envoyes[-1])

    reponse = client.post("/api/mot-de-passe/nouveau", json={"jeton": jeton, "mot_de_passe": "JardinVert2027"})

    assert reponse.status_code == 200
    assert client.get("/api/moi").status_code == 401  # les appareils déjà connectés sont déconnectés
    assert connexion(client, email).status_code == 401  # l'ancien mot de passe ne marche plus
    assert connexion(client, email, "JardinVert2027").status_code == 200


def test_lien_mot_de_passe_valable_1_heure(client, mails_envoyes, base: Session) -> None:
    # RM-COMPTES : lien envoyé à 14 h 00, cliqué à 15 h 10 → expiré
    email = email_essai()
    reponse_inscription(client, email)
    client.post("/api/mot-de-passe/oubli", json={"email": email})
    jeton = jeton_du_mail(mails_envoyes[-1])
    duree = base.execute(
        text("SELECT expire_le - cree_le FROM jeton_mail WHERE usage = 'mot_de_passe' "
             "AND compte_id = (SELECT id FROM compte WHERE email = :e)"),
        {"e": email},
    ).scalar_one()
    base.execute(
        text("UPDATE jeton_mail SET cree_le = now() - interval '70 minutes', expire_le = now() - interval '10 minutes' "
             "WHERE usage = 'mot_de_passe' AND compte_id = (SELECT id FROM compte WHERE email = :e)"),
        {"e": email},
    )
    base.commit()

    reponse = client.post("/api/mot-de-passe/nouveau", json={"jeton": jeton, "mot_de_passe": "JardinVert2027"})

    assert duree == timedelta(hours=1)
    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Ce lien a expiré. Demandez-en un nouveau."


def test_nouveau_mot_de_passe_trop_court_refuse(client, mails_envoyes) -> None:
    email = email_essai()
    reponse_inscription(client, email)
    client.post("/api/mot-de-passe/oubli", json={"email": email})
    jeton = jeton_du_mail(mails_envoyes[-1])

    reponse = client.post("/api/mot-de-passe/nouveau", json={"jeton": jeton, "mot_de_passe": "soleil"})

    assert reponse.status_code == 400
    assert "au moins 10 caractères" in reponse.json()["detail"]


def test_mot_de_passe_jamais_stocke_en_clair(client, mails_envoyes, base: Session) -> None:
    email = email_essai()
    reponse_inscription(client, email)

    hache = base.execute(text("SELECT mot_de_passe_hache FROM compte WHERE email = :e"), {"e": email}).scalar_one()

    assert MOT_DE_PASSE_TEST not in hache
    assert hache.startswith("$argon2")
