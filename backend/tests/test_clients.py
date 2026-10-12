"""Données du client (RM-CLIENTS.md ; lot 2.6) : adresse, informations, export, fermeture, comptes inactifs."""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.services.clients import traiter_inactifs
from tests.conftest import MOT_DE_PASSE_TEST


def commune(client, code_postal: str, nom: str) -> int:
    return next(c["id"] for c in client.get("/api/communes/recherche", params={"q": code_postal}).json() if c["nom"] == nom)


@pytest.fixture
def talence(client) -> int:
    return commune(client, "33400", "Talence")


def adresse(compte, commune_id: int, **modifs):
    donnees = {"ligne": "8 allée des Pins", "complement": "Bâtiment B", "commune_id": commune_id, "code_postal": "33400"} | modifs
    return compte.client.post("/api/moi/adresse", json=donnees)


# ---------- Adresse ----------


def test_mme_dupont_enregistre_son_adresse(fabrique_compte, talence) -> None:
    dupont = fabrique_compte()

    reponse = adresse(dupont, talence)
    relue = dupont.client.get("/api/moi/adresse").json()

    assert reponse.status_code == 200
    assert relue["ligne"] == "8 allée des Pins" and relue["commune"]["nom"] == "Talence" and relue["code_postal"] == "33400"


def test_code_postal_d_une_autre_commune_refuse(fabrique_compte, talence) -> None:
    dupont = fabrique_compte()

    reponse = adresse(dupont, talence, code_postal="33600")  # 33600 = Pessac

    assert reponse.status_code == 400
    assert reponse.json()["detail"] == "Le code postal 33600 ne correspond pas à Talence (33400)."


def test_adresse_trop_courte_refusee(fabrique_compte, talence) -> None:
    reponse = adresse(fabrique_compte(), talence, ligne="8")

    assert reponse.status_code == 400
    assert "entre 3 et 120 caractères" in reponse.json()["detail"]


def test_une_seule_adresse_modifiable_puis_effacable(fabrique_compte, talence, client) -> None:
    dupont = fabrique_compte()
    adresse(dupont, talence)

    adresse(dupont, commune(client, "33600", "Pessac"), ligne="3 rue du Moulin", code_postal="33600")
    apres_modif = dupont.client.get("/api/moi/adresse").json()
    dupont.client.post("/api/moi/adresse/effacer")

    assert apres_modif["ligne"] == "3 rue du Moulin" and apres_modif["commune"]["nom"] == "Pessac"
    assert dupont.client.get("/api/moi/adresse").json() is None


# ---------- Informations ----------


def test_modifier_ses_informations(fabrique_compte) -> None:
    dupont = fabrique_compte()

    ok = dupont.client.post("/api/moi/informations", json={"prenom": "Marie", "nom": "ZZTEST Dupont", "telephone": "07 00 00 00 00"})
    vide = dupont.client.post("/api/moi/informations", json={"prenom": "Marie", "nom": " ", "telephone": "07"})

    assert ok.status_code == 200
    assert dupont.client.get("/api/moi").json()["telephone"] == "07 00 00 00 00"
    assert vide.status_code == 400 and vide.json()["detail"] == "Le nom est obligatoire."


# ---------- Télécharger mes données ----------


def test_telecharger_mes_donnees(fabrique_compte, talence) -> None:
    dupont = fabrique_compte()
    adresse(dupont, talence)

    reponse = dupont.client.get("/api/moi/donnees")
    donnees = reponse.json()

    assert "attachment" in reponse.headers["content-disposition"]
    assert donnees["compte"]["email"] == dupont.email
    assert donnees["adresse"]["commune"] == "Talence"
    assert "mot_de_passe" not in reponse.text and "jeton" not in reponse.text  # aucun secret dans le fichier
    assert any(ligne["action"] == "enregistrer_adresse" for ligne in donnees["journal_de_mes_actions"])


# ---------- Fermer son compte ----------


def test_fermer_son_compte_efface_tout_ce_qui_est_personnel(fabrique_compte, talence, base: Session, client) -> None:
    dupont = fabrique_compte()
    adresse(dupont, talence)

    mauvais = dupont.client.post("/api/moi/fermer", json={"mot_de_passe": "PasLeBonDuTout"})
    ferme = dupont.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})
    ligne = base.execute(
        text("SELECT email, prenom, nom, telephone, date_naissance, ferme_le IS NOT NULL FROM compte WHERE id = :id"),
        {"id": dupont.id},
    ).one()
    adresses = base.execute(text("SELECT count(*) FROM adresse WHERE compte_id = :id"), {"id": dupont.id}).scalar_one()

    assert mauvais.status_code == 403
    assert ferme.status_code == 200
    # Compte d'essai (@example.com) : il garde la marque d'essai pour le nettoyage ; un vrai compte → @rafals.invalid
    assert tuple(ligne) == (f"compte-ferme-{dupont.id}@example.com", "Compte", "fermé", None, None, True)
    assert adresses == 0
    assert dupont.client.get("/api/moi").status_code == 401  # déconnecté partout
    connexion = client.post("/api/connexion", json={"email": dupont.email, "mot_de_passe": MOT_DE_PASSE_TEST})
    assert connexion.status_code == 401


def test_prestataire_en_activite_doit_d_abord_arreter(fabrique_compte, client, talence) -> None:
    karim = fabrique_compte()
    plombier = next(m["id"] for m in client.get("/api/metiers/recherche", params={"q": "plombier"}).json() if m["nom"] == "Plombier")
    karim.client.post("/api/moi/prestataire", json={"nom_affiche": "Karim", "metier_principal_id": plombier, "commune_id": talence, "distance_km": 10})

    refus = karim.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})
    karim.client.post("/api/moi/prestataire/statut", json={"action": "arreter"})
    ok = karim.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})

    assert refus.status_code == 400 and "Arrêtez d'abord votre activité" in refus.json()["detail"]
    assert ok.status_code == 200


def test_le_seul_administrateur_ne_peut_pas_fermer_son_compte(fabrique_compte, base: Session) -> None:
    raphael = fabrique_compte(administrateur=True)
    base.execute(text("UPDATE compte SET est_administrateur = false WHERE id <> :id"), {"id": raphael.id})
    base.commit()

    reponse = raphael.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})

    assert reponse.status_code == 400
    assert "seul administrateur" in reponse.json()["detail"]


# ---------- Comptes inactifs ----------


def vieillir(base: Session, compte_id: int, **dates: datetime) -> None:
    for colonne, valeur in dates.items():
        base.execute(text(f"UPDATE compte SET {colonne} = :v WHERE id = :id"), {"v": valeur, "id": compte_id})
    base.commit()


def test_inactif_3_ans_prevenu_puis_ferme_30_jours_apres(fabrique_compte, base: Session, mails_envoyes) -> None:
    # RM-CLIENTS : dernière connexion le 10/01/2027 → mail le 10/01/2030 → fermeture le 09/02/2030
    maintenant = datetime.now(UTC)
    endormi = fabrique_compte()
    vieillir(base, endormi.id, derniere_connexion_le=maintenant - timedelta(days=3 * 365 + 1))

    traiter_inactifs(base, maintenant)
    base.commit()
    prevenu = [m for m in mails_envoyes if m["a"] == endormi.email and "sera fermé" in m["sujet"]]
    vieillir(base, endormi.id, inactivite_prevenue_le=maintenant - timedelta(days=31))
    traiter_inactifs(base, maintenant)
    base.commit()
    ferme = base.execute(text("SELECT ferme_le IS NOT NULL FROM compte WHERE id = :id"), {"id": endormi.id}).scalar_one()

    assert len(prevenu) == 1 and "sera fermé dans 30 jours" in prevenu[0]["sujet"]
    assert ferme is True


def test_se_reconnecter_annule_la_fermeture(fabrique_compte, base: Session, client, mails_envoyes) -> None:
    maintenant = datetime.now(UTC)
    endormi = fabrique_compte()
    vieillir(base, endormi.id, derniere_connexion_le=maintenant - timedelta(days=3 * 365 + 1))
    traiter_inactifs(base, maintenant)
    base.commit()

    client.post("/api/connexion", json={"email": endormi.email, "mot_de_passe": MOT_DE_PASSE_TEST})
    base.expire_all()
    prevenu = base.execute(text("SELECT inactivite_prevenue_le FROM compte WHERE id = :id"), {"id": endormi.id}).scalar_one()

    assert prevenu is None


def test_un_compte_actif_n_est_jamais_prevenu(fabrique_compte, base: Session, mails_envoyes) -> None:
    actif = fabrique_compte()  # vient de se connecter

    traiter_inactifs(base, datetime.now(UTC))
    base.commit()

    assert not [m for m in mails_envoyes if m["a"] == actif.email and "sera fermé" in m["sujet"]]


# ---------- Prestataire : « Mon adresse » est aussi l'adresse de son local (07/10/2026) ----------


def test_adresse_du_prestataire_est_aussi_son_local(fabrique_compte, client) -> None:
    from tests.test_prestataires import devenir, id_commune, id_metier

    def local(compte) -> list[dict]:
        return compte.client.get("/api/moi/donnees").json()["profil_prestataire"]["local"]

    karim = fabrique_compte()
    pessac = id_commune(client, "33600", "Pessac")
    devenir(karim, {"nom_affiche": "ZZTEST Karim", "metier_principal_id": id_metier(client, "Plombier"),
                    "commune_id": pessac, "distance_km": 15, "metiers_secondaires": []})
    assert local(karim) == []

    depot = karim.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": pessac, "code_postal": "33600"})

    assert depot.status_code == 200, depot.text
    assert local(karim)[0]["ligne"] == "3 rue du Moulin" and local(karim)[0]["code_postal"] == "33600"

    karim.client.post("/api/moi/adresse", json={"ligne": "9 avenue Jean Jaurès", "commune_id": pessac, "code_postal": "33600"})
    assert local(karim)[0]["ligne"] == "9 avenue Jean Jaurès"

    karim.client.post("/api/moi/adresse/effacer")
    assert karim.client.get("/api/moi/adresse").json() is None and local(karim) == []


def test_adresse_d_un_client_ne_cree_aucun_local(fabrique_compte, client, base: Session) -> None:
    from tests.test_prestataires import id_commune

    julie = fabrique_compte()
    avant = base.execute(text("SELECT count(*) FROM local")).scalar_one()

    julie.client.post("/api/moi/adresse", json={"ligne": "8 allée des Pins", "commune_id": id_commune(client, "33400", "Talence"),
                                                "code_postal": "33400"})

    assert base.execute(text("SELECT count(*) FROM local")).scalar_one() == avant
