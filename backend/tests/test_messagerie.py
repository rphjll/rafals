"""Messagerie (RM-MESSAGERIE.md ; lot 8.1) : une conversation par couple, qui peut commencer, messages et photos,
coordonnées masquées avant le premier rendez-vous, lu / non lu, mail après 15 minutes, bloquer, signaler."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services import messagerie
from tests.conftest import MOT_DE_PASSE_TEST
from tests.test_agenda import MARDI, lea  # noqa: F401 (fixtures)
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_prestataires import JPG, PDF
from tests.test_rendez_vous import a, dupont, reserver  # noqa: F401 (fixtures)


def id_prestataire(compte) -> int:
    return compte.client.get("/api/moi/prestataire").json()["id"]


def commencer(client_compte, prestataire_compte) -> dict:
    """[Écrire à Léa] : la cliente ouvre la conversation."""
    reponse = client_compte.client.post("/api/conversations", json={"prestataire_id": id_prestataire(prestataire_compte)})
    assert reponse.status_code == 201, reponse.text
    return reponse.json()


def ecrire(compte, conversation_id: int, texte: str = "", photos: list[tuple] | None = None):
    fichiers = [("photos", (nom, contenu, type_mime)) for nom, contenu, type_mime in photos or []]
    return compte.client.post(f"/api/conversations/{conversation_id}/messages", data={"texte": texte}, files=fichiers or None)


def lire(compte, conversation_id: int) -> dict:
    return compte.client.get(f"/api/conversations/{conversation_id}").json()


def vieillir(base: Session, conversation_id: int, minutes: int) -> None:
    """Fait comme si tout s'était passé quelques minutes plus tôt : les messages écrits, et les lectures."""
    base.execute(text("UPDATE message SET cree_le = cree_le - make_interval(mins => :m) WHERE conversation_id = :id"),
                 {"m": minutes, "id": conversation_id})
    base.execute(text("UPDATE conversation SET client_lu_le = client_lu_le - make_interval(mins => :m),"
                      " prestataire_lu_le = prestataire_lu_le - make_interval(mins => :m) WHERE id = :id"),
                 {"m": minutes, "id": conversation_id})
    base.commit()


# ---------- Commencer une conversation ----------


def test_une_seule_conversation_par_couple(lea, dupont) -> None:
    premiere = commencer(dupont, lea)
    seconde = commencer(dupont, lea)

    assert premiere["id"] == seconde["id"] and premiere["cote"] == "client" and premiere["avec"] == "Karim Benali"
    assert len(dupont.client.get("/api/moi/conversations").json()) == 1


def test_le_prestataire_voit_le_client_sans_son_nom_complet(lea, dupont) -> None:
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Faites-vous les chignons de mariage ?")

    vue = lea.client.get("/api/moi/conversations").json()[0]

    assert vue["cote"] == "prestataire" and vue["avec"] == "Essai Z." and "ZZTEST" not in str(vue)
    assert vue["apercu"] == "Faites-vous les chignons de mariage ?" and vue["non_lus"] == 1


def test_un_prestataire_n_ecrit_pas_en_premier_a_un_inconnu(lea, dupont) -> None:
    inconnu = lea.client.post("/api/conversations", json={"client_id": dupont.id})
    reserver(dupont, lea, a(MARDI, 10))
    apres_un_rendez_vous = lea.client.post("/api/conversations", json={"client_id": dupont.id})

    assert inconnu.status_code == 403 and "rendez-vous ou un devis" in inconnu.json()["detail"]
    assert apres_un_rendez_vous.status_code == 201 and apres_un_rendez_vous.json()["cote"] == "prestataire"


def test_on_ne_s_ecrit_pas_a_soi_meme_ni_a_un_prestataire_en_pause(lea, dupont) -> None:
    soi_meme = lea.client.post("/api/conversations", json={"prestataire_id": id_prestataire(lea)})
    lea.client.post("/api/moi/prestataire/statut", json={"action": "pause"})
    en_pause = dupont.client.post("/api/conversations", json={"prestataire_id": id_prestataire(lea)})

    assert soi_meme.status_code == 400 and "vous-même" in soi_meme.json()["detail"]
    assert en_pause.status_code == 400 and "pas joignable" in en_pause.json()["detail"]


def test_un_autre_ne_lit_pas_ma_conversation(lea, dupont, fabrique_compte) -> None:
    conversation = commencer(dupont, lea)
    curieux = fabrique_compte()

    assert curieux.client.get(f"/api/conversations/{conversation['id']}").status_code == 404
    assert ecrire(curieux, conversation["id"], "Bonjour").status_code == 404
    assert curieux.client.get("/api/moi/conversations").json() == []
    assert fabrique_compte().client.get("/api/conversations/999999").status_code == 404


# ---------- Écrire ----------


def test_ecrire_lire_et_compteur_rouge(lea, dupont) -> None:
    conversation = commencer(dupont, lea)
    envoi = ecrire(dupont, conversation["id"], "  Bonjour, êtes-vous libre samedi ?  ")
    avant = lea.client.get("/api/moi/conversations/non-lues").json()["nombre"]
    pas_encore_lu = lire(dupont, conversation["id"])["messages"][0]["lu"]
    vue_par_lea = lire(lea, conversation["id"])  # ouvrir = lire
    apres = lea.client.get("/api/moi/conversations/non-lues").json()["nombre"]
    ecrire(lea, conversation["id"], "Oui, à 10 h.")
    fil = lire(dupont, conversation["id"])["messages"]

    assert envoi.status_code == 201 and envoi.json()["messages"][0]["texte"] == "Bonjour, êtes-vous libre samedi ?"
    assert (avant, apres) == (1, 0) and pas_encore_lu is False
    assert vue_par_lea["messages"][0]["de_moi"] is False
    assert [(m["de_moi"], m["texte"]) for m in fil] == [(True, "Bonjour, êtes-vous libre samedi ?"), (False, "Oui, à 10 h.")]
    assert fil[0]["lu"] is True  # Léa a ouvert la conversation


def test_message_vide_trop_long_ou_injurieux_refuse(lea, dupont, base: Session) -> None:
    conversation = commencer(dupont, lea)
    base.execute(text("INSERT INTO mot_interdit (mot) VALUES ('zzgrosmot') ON CONFLICT DO NOTHING"))
    base.commit()

    vide = ecrire(dupont, conversation["id"], "   ")
    trop_long = ecrire(dupont, conversation["id"], "a" * (reglages.MESSAGE_TEXTE_MAX + 1))
    gros_mot = ecrire(dupont, conversation["id"], "Vous êtes une zzgrosmot")
    injure = ecrire(dupont, conversation["id"], "Une arnaqueuse ZZINJURE qui profite des vieux")

    assert vide.status_code == 400 and "Écrivez un message" in vide.json()["detail"]
    assert trop_long.status_code == 400 and "2000" in trop_long.json()["detail"]
    assert gros_mot.status_code == 400 and "mot interdit" in gros_mot.json()["detail"]
    assert injure.status_code == 400 and "injurieux" in injure.json()["detail"]
    assert lire(dupont, conversation["id"])["messages"] == []


def test_photos_cinq_au_plus_vues_par_les_deux_seulement(lea, dupont, fabrique_compte) -> None:
    conversation = commencer(dupont, lea)
    photo = lambda n: (f"fuite{n}.jpg", JPG + bytes([n]), "image/jpeg")  # noqa: E731

    seule = ecrire(dupont, conversation["id"], "", [photo(1), photo(2)])  # des photos sans texte : accepté
    six = ecrire(dupont, conversation["id"], "Voilà", [photo(n) for n in range(10, 16)])
    pdf = ecrire(dupont, conversation["id"], "Voilà", [("devis.pdf", PDF, "application/pdf")])
    message = seule.json()["messages"][0]

    assert seule.status_code == 201 and message["nombre_photos"] == 2 and seule.json()["apercu"] == "Photo"
    assert six.status_code == 400 and "5 photos" in six.json()["detail"] and pdf.status_code == 400
    assert lea.client.get(f"/api/messages/{message['id']}/photos/2").content == JPG + bytes([2])
    assert fabrique_compte().client.get(f"/api/messages/{message['id']}/photos/1").status_code == 404
    assert dupont.client.get(f"/api/messages/{message['id']}/photos/3").status_code == 404


# ---------- Coordonnées masquées avant le premier rendez-vous ----------


def test_coordonnees_masquees_puis_visibles_apres_la_reservation(lea, dupont) -> None:
    conversation = commencer(dupont, lea)
    ecrire(lea, conversation["id"], "Appelez-moi au 06 12 34 56 78 ou écrivez à lea@exemple.fr, merci")

    avant = lire(dupont, conversation["id"])
    apercu_avant = dupont.client.get("/api/moi/conversations").json()[0]["apercu"]
    reserver(dupont, lea, a(MARDI, 10))
    apres = lire(dupont, conversation["id"])

    assert avant["coordonnees_masquees"] is True
    assert "06 12" not in avant["messages"][0]["texte"] and "lea@" not in avant["messages"][0]["texte"]
    assert avant["messages"][0]["texte"].count("(coordonnées masquées jusqu'à la réservation)") == 2
    assert "06 12" not in apercu_avant
    assert apres["coordonnees_masquees"] is False and "06 12 34 56 78" in apres["messages"][0]["texte"]


def test_masquer_les_formes_courantes() -> None:
    masque = messagerie.MASQUE

    assert messagerie.masquer("au 0612345678.") == f"au {masque}."
    assert messagerie.masquer("mon +33 6 12 34 56 78") == f"mon {masque}"
    assert messagerie.masquer("tom.l+pro@mail.example.com !") == f"{masque} !"
    assert messagerie.masquer("Rendez-vous à 10 h, 200 m², 35 €, le 12/10/2026") == "Rendez-vous à 10 h, 200 m², 35 €, le 12/10/2026"


# ---------- Mail après 15 minutes sans lecture ----------


def test_mail_seulement_si_pas_lu_au_bout_de_15_minutes(lea, dupont, base: Session, mails_envoyes) -> None:
    recus = lambda: [m for m in mails_envoyes if m["a"] == lea.email and "vous a écrit" in m["sujet"]]  # noqa: E731
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Bonjour, êtes-vous libre samedi ?")
    maintenant = datetime.now(UTC)

    messagerie.prevenir_par_mail(base, maintenant)
    trop_tot = len(recus())
    vieillir(base, conversation["id"], 20)
    messagerie.prevenir_par_mail(base, maintenant)
    base.commit()
    envoye = len(recus())
    messagerie.prevenir_par_mail(base, maintenant)
    deux_fois = len(recus())

    assert (trop_tot, envoye, deux_fois) == (0, 1, 1)
    assert "Essai Z." in recus()[0]["sujet"] and "samedi" not in recus()[0]["texte"]  # le message n'est pas recopié


def test_pas_de_mail_si_le_message_est_lu_ni_deux_dans_l_heure(lea, dupont, base: Session, mails_envoyes) -> None:
    # (la base de test contient aussi les conversations des autres tests : on compte les mails reçus par Léa)
    recus = lambda: len([m for m in mails_envoyes if m["a"] == lea.email and "vous a écrit" in m["sujet"]])  # noqa: E731
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Bonjour")
    lire(lea, conversation["id"])  # Léa lit tout de suite
    vieillir(base, conversation["id"], 20)
    messagerie.prevenir_par_mail(base, datetime.now(UTC))
    lu = recus()

    ecrire(dupont, conversation["id"], "Vous êtes là ?")
    vieillir(base, conversation["id"], 20)
    messagerie.prevenir_par_mail(base, datetime.now(UTC))
    base.commit()
    premier = recus()
    ecrire(dupont, conversation["id"], "Allô ?")
    vieillir(base, conversation["id"], 20)
    messagerie.prevenir_par_mail(base, datetime.now(UTC))
    dans_l_heure = recus()
    messagerie.prevenir_par_mail(base, datetime.now(UTC) + reglages.MESSAGE_MAIL_ECART)
    plus_tard = recus()

    assert (lu, premier, dans_l_heure, plus_tard) == (0, 1, 1, 2)


# ---------- Bloquer, signaler ----------


def test_bloquer_arrete_les_messages_dans_les_deux_sens(lea, dupont) -> None:
    conversation = commencer(dupont, lea)
    bloquee = dupont.client.post(f"/api/conversations/{conversation['id']}/bloquer").json()
    de_lea = ecrire(lea, conversation["id"], "Bonjour")
    de_dupont = ecrire(dupont, conversation["id"], "Bonjour")
    par_l_autre = lea.client.post(f"/api/conversations/{conversation['id']}/debloquer")
    debloquee = dupont.client.post(f"/api/conversations/{conversation['id']}/debloquer").json()

    assert bloquee["bloquee"] is True and bloquee["bloquee_par_moi"] is True
    assert de_lea.status_code == 400 and de_dupont.status_code == 400 and "bloquée" in de_lea.json()["detail"]
    assert par_l_autre.status_code == 403 and debloquee["bloquee"] is False
    assert ecrire(lea, conversation["id"], "Bonjour").status_code == 201


def test_l_administrateur_ne_lit_qu_une_conversation_signalee(lea, dupont, fabrique_compte, mails_envoyes) -> None:
    conversation = commencer(dupont, lea)
    ecrire(lea, conversation["id"], "Payez-moi 50 € avant que je vienne, au 06 12 34 56 78")
    admin = fabrique_compte(administrateur=True)
    adresse = f"/api/admin/conversations/{conversation['id']}"

    avant = admin.client.get(adresse)
    trop_court = dupont.client.post(f"/api/conversations/{conversation['id']}/signaler", json={"motif": "Nul"})
    signalee = dupont.client.post(f"/api/conversations/{conversation['id']}/signaler",
                                  json={"motif": "Elle insiste pour être payée avant de venir"})
    deux_fois = dupont.client.post(f"/api/conversations/{conversation['id']}/signaler",
                                   json={"motif": "Elle insiste encore pour être payée avant"})
    fil = admin.client.get(adresse)
    liste = [s for s in admin.client.get("/api/admin/signalements").json() if s["conversation_id"] == conversation["id"]]
    prevenue = admin.client.post(f"/api/admin/signalements/{liste[0]['id']}", json={"action": "prevenir", "decision": "Pas de paiement d'avance"})

    assert avant.status_code == 404 and "pas été signalée" in avant.json()["detail"]
    assert trop_court.status_code == 400 and signalee.status_code == 201 and deux_fois.status_code == 400
    # L'administrateur lit le fil en clair (il doit pouvoir juger)
    assert fil.status_code == 200 and "06 12 34 56 78" in fil.json()["messages"][0]["texte"]
    assert fil.json()["messages"][0]["auteur"] == "Karim Benali"
    assert dupont.client.get(adresse).status_code == 403
    assert len(liste) == 1 and liste[0]["prestataire"] == "Karim Benali"
    assert prevenue.status_code == 200 and prevenue.json()["statut"] == "suivi"
    assert any(m["a"] == lea.email and "Pas de paiement d'avance" in m["texte"] for m in mails_envoyes)


def test_un_prestataire_signale_un_client(lea, dupont, fabrique_compte, mails_envoyes) -> None:
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Vous venez gratuitement, sinon je mets un mauvais avis")
    lea.client.post(f"/api/conversations/{conversation['id']}/signaler", json={"motif": "Le client me menace d'un mauvais avis"})
    admin = fabrique_compte(administrateur=True)

    vu = next(s for s in admin.client.get("/api/admin/signalements").json() if s["conversation_id"] == conversation["id"])
    bloquer = admin.client.post(f"/api/admin/signalements/{vu['id']}", json={"action": "bloquer_prestataire", "decision": "Menaces"})
    prevenir = admin.client.post(f"/api/admin/signalements/{vu['id']}", json={"action": "prevenir", "decision": "Restez courtois"})

    assert vu["prestataire_id"] is None and vu["prestataire"] == "Essai ZZTEST (client)"
    assert bloquer.status_code == 400 and "vise un client" in bloquer.json()["detail"]
    assert prevenir.status_code == 200 and any(m["a"] == dupont.email and "Restez courtois" in m["texte"] for m in mails_envoyes)


# ---------- Données personnelles ----------


def test_conversation_effacee_apres_3_ans_sans_message(lea, dupont, base: Session) -> None:
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Bonjour", [("a.jpg", JPG, "image/jpeg")])
    maintenant = datetime.now(UTC)

    trop_tot = messagerie.effacer_les_anciennes(base, maintenant + reglages.MESSAGE_CONSERVATION - timedelta(days=1))
    effacees = messagerie.effacer_les_anciennes(base, maintenant + reglages.MESSAGE_CONSERVATION + timedelta(days=1))
    base.commit()

    # (la base de test contient aussi les conversations des autres tests : on vérifie la nôtre)
    assert trop_tot == 0 and effacees >= 1
    assert dupont.client.get("/api/moi/conversations").json() == []


def test_compte_ferme_les_messages_restent_sans_le_nom(lea, dupont) -> None:
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Bonjour, merci pour tout")
    dupont.client.post("/api/moi/fermer", json={"mot_de_passe": MOT_DE_PASSE_TEST})

    vue = lire(lea, conversation["id"])
    refus = ecrire(lea, conversation["id"], "Au revoir")

    assert vue["avec"] == "Personne ayant quitté rafals" and vue["messages"][0]["texte"] == "Bonjour, merci pour tout"
    assert refus.status_code == 400 and "a quitté rafals" in refus.json()["detail"]


def test_mes_conversations_dans_telecharger_mes_donnees(lea, dupont) -> None:
    conversation = commencer(dupont, lea)
    ecrire(dupont, conversation["id"], "Bonjour, êtes-vous libre samedi ?")

    donnees = dupont.client.get("/api/moi/donnees").json()

    assert donnees["conversations"] == [{"avec": "Karim Benali", "messages": [
        {"de_moi": True, "texte": "Bonjour, êtes-vous libre samedi ?", "le": donnees["conversations"][0]["messages"][0]["le"]}]}]
