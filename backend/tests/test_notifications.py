"""Notifications sur le téléphone (RM-ALERTES.md, RM-APPLICATION.md ; lot 8.7, 2e partie) : un appareil donne son
accord, reçoit les nouvelles demandes, les messages et les étapes d'une proposition, sans nom complet ni texte du
message ; on peut couper, un appareil disparu s'efface, un compte fermé n'a plus d'appareil."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import config
from tests.conftest import MOT_DE_PASSE_TEST
from tests.test_demandes import pelouse, publier
from tests.test_messagerie import commencer, ecrire
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_propositions import accepter, fuite, proposition_de_karim  # noqa: F401 (fixtures)


def activer(compte, numero: int = 1):
    """Ce que le navigateur donne quand on clique « Autoriser » (adresse d'essai marquée zztest)."""
    return compte.client.post("/api/moi/appareils", json={
        "adresse": f"https://zztest.example.com/push/{compte.id}-{numero}",
        "cle_publique": "BOr3zztestClePubliqueDuTelephone", "cle_secrete": "k2QazztestSecret"})


def appareils(base: Session, compte) -> int:
    return base.execute(text("SELECT count(*) FROM appareil WHERE compte_id = :id"), {"id": compte.id}).scalar_one()


def test_activer_puis_couper(fabrique_compte, client, base: Session, notifications_envoyees, monkeypatch) -> None:
    dupont, autre = fabrique_compte(), fabrique_compte()
    adresse = f"https://zztest.example.com/push/{dupont.id}-1"

    cle = client.get("/api/notifications/cle").json()
    active = activer(dupont)
    etat = dupont.client.post("/api/moi/appareils/etat", json={"adresse": adresse}).json()
    vu_par_un_autre = autre.client.post("/api/moi/appareils/etat", json={"adresse": adresse}).json()
    deux_fois = activer(dupont)
    nombre = appareils(base, dupont)
    coupe = dupont.client.post("/api/moi/appareils/couper", json={"adresse": adresse})
    apres = dupont.client.post("/api/moi/appareils/etat", json={"adresse": adresse}).json()
    monkeypatch.setattr(config, "VAPID_PRIVEE", "")
    sans_cle = client.get("/api/notifications/cle").json()

    assert cle == {"cle": "zztest-cle-publique"} and sans_cle == {"cle": None}
    assert active.status_code == 200 and active.json()["message"] == "Notifications activées sur cet appareil."
    # Une notification d'essai tout de suite, pour voir que ça marche
    assert notifications_envoyees.pour(dupont.id)[0] == "Les notifications sont activées sur cet appareil."
    assert etat == {"active": True} and vu_par_un_autre == {"active": False}
    assert deux_fois.status_code == 200 and nombre == 1  # le même téléphone n'est jamais enregistré deux fois
    assert coupe.status_code == 200 and apres == {"active": False} and appareils(base, dupont) == 0


def test_nouvelle_demande_meme_sans_mail(fabrique_prestataire, fabrique_compte, metiers, notifications_envoyees) -> None:  # noqa: F811
    karim, coiffeuse, dupont = fabrique_prestataire(), fabrique_prestataire("Coiffeur", ()), fabrique_compte()
    activer(karim)
    activer(coiffeuse)
    karim.client.post("/api/moi/prestataire/alertes", json={"alerte_mail": "aucun", "metiers_coupes": [metiers["Électricien"]]})

    publier(dupont, pelouse(metiers["Plombier"], titre="Fuite sous l'évier"))
    publier(dupont, pelouse(metiers["Électricien"], titre="Prise qui disjoncte"))

    nouvelles = [n for n in notifications_envoyees.envoyees if n["titre"] == "Nouvelle demande"]
    # « Aucun mail » ne coupe pas le téléphone ; « Ne pas me prévenir » pour Électricien, si
    assert [(n["compte_id"], n["texte"], n["lien"]) for n in nouvelles] == [
        (karim.id, "Fuite sous l'évier, Pessac (0 km)", "/demandes-pres-de-chez-moi")]


def test_message_et_proposition(fabrique_prestataire, fuite, notifications_envoyees) -> None:  # noqa: F811
    karim = fabrique_prestataire()
    activer(karim)
    activer(fuite)

    proposition = proposition_de_karim(karim, fuite)
    conversation = proposition["conversation_id"]
    ecrire(fuite, conversation, "Bonjour, vous passez par le garage ?")
    accepter(fuite, proposition["id"])

    pour_dupont = notifications_envoyees.pour(fuite.id)
    pour_karim = notifications_envoyees.pour(karim.id)
    assert any(t.endswith("a répondu à votre demande") for t in pour_dupont)
    assert any(t.endswith("vous fait une proposition") for t in pour_dupont)
    # Le message n'est jamais recopié, ni le nom complet
    ecrit = next(n for n in notifications_envoyees.envoyees if n["compte_id"] == karim.id and n["texte"].endswith("vous a écrit"))
    assert "garage" not in ecrit["texte"] and ecrit["lien"] == f"/messages/{conversation}"
    assert any(t.startswith(ecrit["texte"].split(" vous")[0] + " a accepté votre proposition") for t in pour_karim)


def test_appareil_disparu_et_compte_ferme(fabrique_compte, fabrique_prestataire, base: Session, notifications_envoyees) -> None:  # noqa: F811
    karim, dupont = fabrique_prestataire(), fabrique_compte()
    activer(karim, 1)
    activer(karim, 2)
    activer(dupont)
    notifications_envoyees.disparues.add(f"https://zztest.example.com/push/{karim.id}-1")

    conversation = commencer(dupont, karim)["id"]
    ecrire(dupont, conversation, "Bonjour")
    reste_a_karim = appareils(base, karim)
    ferme = dupont.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})

    assert reste_a_karim == 1  # le téléphone changé s'efface, l'ordinateur reste
    assert ferme.status_code == 200 and appareils(base, dupont) == 0
