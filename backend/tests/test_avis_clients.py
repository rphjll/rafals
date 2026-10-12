"""Notation dans les deux sens (RM-AVIS.md § « Notation dans les deux sens » ; lot 8.5) : le prestataire note le client
après un rendez-vous tenu ; page publique du client ; « Mes avis reçus » : répondre une fois, signaler ; l'administrateur
cache ; la note à côté du nom ; la carte « noter » d'une conversation."""

from sqlalchemy import text
from sqlalchemy.orm import Session

from tests.test_agenda import lea  # noqa: F401 (fixture)
from tests.test_avis import rdv_tenu  # noqa: F401 (fixture)
from tests.test_prestataires import fabrique_prestataire, metiers  # noqa: F401 (fixtures)
from tests.test_rendez_vous import dupont  # noqa: F401 (fixture)


def noter(prestataire, rdv_id: int, note: int = 5, texte: str = "Accueillante, la demande était bien décrite, payé tout de suite."):
    return prestataire.client.post(f"/api/moi/prestataire/rendez-vous/{rdv_id}/avis-client", json={"note": note, "texte": texte})


def page(client, compte) -> dict:
    return client.get(f"/api/clients/{compte.id}/avis").json()


def test_le_prestataire_note_le_client(lea, dupont, rdv_tenu, client, mails_envoyes) -> None:  # noqa: F811
    avant = page(client, dupont)
    reponse = noter(lea, rdv_tenu, 5)
    apres = page(client, dupont)

    assert avant["nom"] == "Essai Z." and avant["note"] is None and avant["nombre_avis"] == 0 and avant["avis"] == []
    assert reponse.status_code == 201, reponse.text
    assert apres["note"] == 5.0 and apres["nombre_avis"] == 1 and apres["membre_depuis"]
    assert apres["avis"][0]["auteur"] == "Karim Benali" and apres["avis"][0]["note"] == 5 and apres["avis"][0]["reponse"] is None
    # La page publique ne montre jamais le nom complet, le mail ni le téléphone
    assert "ZZTEST" not in str(apres) and "example.com" not in str(apres) and "0600000000" not in str(apres)
    assert any("vous a laissé un avis" in m["sujet"] for m in mails_envoyes if m["a"] == dupont.email)
    # Le prestataire retrouve son avis sur la ligne du rendez-vous
    recu = next(r for r in lea.client.get("/api/moi/prestataire/rendez-vous").json() if r["id"] == rdv_tenu)
    assert recu["avis_client"]["note"] == 5 and recu["peut_noter_client"] is False


def test_refus_de_noter(lea, dupont, rdv_tenu, fabrique_prestataire, base: Session) -> None:  # noqa: F811
    autre = fabrique_prestataire()

    par_un_autre = noter(autre, rdv_tenu)
    note_zero = noter(lea, rdv_tenu, 0)
    trop_court = noter(lea, rdv_tenu, 4, "Bien")
    injure = noter(lea, rdv_tenu, 1, "Une ZZINJURE, à éviter absolument.")
    premiere = noter(lea, rdv_tenu, 4)
    deux_fois = noter(lea, rdv_tenu, 2)

    assert par_un_autre.status_code == 404
    assert note_zero.status_code == 400 and "1 à 5 étoiles" in note_zero.json()["detail"]
    assert trop_court.status_code == 400 and "entre 10 et 500" in trop_court.json()["detail"]
    assert injure.status_code == 400 and premiere.status_code == 201
    assert deux_fois.status_code == 400 and "déjà noté" in deux_fois.json()["detail"]


def test_pas_d_avis_apres_30_jours_ni_avec_une_absence(lea, dupont, rdv_tenu, base: Session) -> None:  # noqa: F811
    base.execute(text("UPDATE rendez_vous SET absent = 'client', absence_signalee_le = now() WHERE id = :id"), {"id": rdv_tenu})
    base.commit()
    avec_absence = noter(lea, rdv_tenu)
    base.execute(text("UPDATE rendez_vous SET absent = NULL, absence_signalee_le = NULL, debut = debut - interval '40 days',"
                      " fin = fin - interval '40 days' WHERE id = :id"), {"id": rdv_tenu})
    base.commit()
    trop_tard = noter(lea, rdv_tenu)

    assert avec_absence.status_code == 400 and trop_tard.status_code == 400 and "dans les 30 jours" in trop_tard.json()["detail"]


def test_modifier_puis_retirer(lea, dupont, rdv_tenu, client) -> None:  # noqa: F811
    avis = noter(lea, rdv_tenu, 2, "Pelouse deux fois plus grande qu'annoncé.").json()

    modifie = lea.client.post(f"/api/moi/prestataire/avis-clients/{avis['id']}/modifier", json={"note": 4, "texte": "Finalement très correcte, merci."})
    par_la_cliente = dupont.client.post(f"/api/moi/prestataire/avis-clients/{avis['id']}/modifier", json={"note": 5, "texte": "Je suis parfaite, bien sûr."})
    note_apres = page(client, dupont)["note"]
    retire = lea.client.post(f"/api/moi/prestataire/avis-clients/{avis['id']}/retirer")

    assert modifie.status_code == 200 and note_apres == 4.0 and par_la_cliente.status_code == 404
    assert retire.status_code == 200 and retire.json()["retire"] is True
    assert page(client, dupont)["nombre_avis"] == 0 and dupont.client.get("/api/moi/avis-recus").json() == []


def test_mes_avis_recus_repondre_une_fois_et_compteur(lea, dupont, rdv_tenu, client) -> None:  # noqa: F811
    avis = noter(lea, rdv_tenu, 3, "Un peu en retard à l'ouverture de la porte.").json()

    non_vus = dupont.client.get("/api/moi/avis-recus/non-vus").json()["nombre"]
    recus = dupont.client.get("/api/moi/avis-recus").json()
    apres_lecture = dupont.client.get("/api/moi/avis-recus/non-vus").json()["nombre"]
    reponse = dupont.client.post(f"/api/moi/avis-recus/{avis['id']}/repondre", json={"texte": "J'étais au téléphone, désolée."})
    deuxieme = dupont.client.post(f"/api/moi/avis-recus/{avis['id']}/repondre", json={"texte": "Encore moi"})
    par_lea = lea.client.post(f"/api/moi/avis-recus/{avis['id']}/repondre", json={"texte": "Ce n'est pas à moi de répondre."})

    assert non_vus == 1 and apres_lecture == 0
    assert len(recus) == 1 and recus[0]["note"] == 3 and recus[0]["auteur"] == "Karim Benali" and recus[0]["titre"]
    assert reponse.status_code == 200 and deuxieme.status_code == 400 and par_lea.status_code == 404
    assert page(client, dupont)["avis"][0]["reponse"] == "J'étais au téléphone, désolée."


def test_signaler_puis_l_administrateur_cache(lea, dupont, rdv_tenu, fabrique_compte, client, mails_envoyes) -> None:  # noqa: F811
    admin = fabrique_compte(administrateur=True)
    avis = noter(lea, rdv_tenu, 1, "Cliente très désagréable, à éviter.").json()

    sans_raison = dupont.client.post(f"/api/moi/avis-recus/{avis['id']}/signaler", json={"texte": "non"})
    signale = dupont.client.post(f"/api/moi/avis-recus/{avis['id']}/signaler", json={"texte": "Fausse accusation, il n'est jamais venu."})
    deux_fois = dupont.client.post(f"/api/moi/avis-recus/{avis['id']}/signaler", json={"texte": "Fausse accusation encore."})
    liste = [s for s in admin.client.get("/api/admin/avis-clients-signales").json() if s["avis"]["id"] == avis["id"]]
    par_un_client = dupont.client.get("/api/admin/avis-clients-signales")
    sans_motif = admin.client.post(f"/api/admin/avis-clients/{avis['id']}/decision", json={"cacher": True})
    cache = admin.client.post(f"/api/admin/avis-clients/{avis['id']}/decision", json={"cacher": True, "motif": "Accusation sans élément."})

    assert sans_raison.status_code == 400 and signale.status_code == 200 and signale.json()["signale"] is True
    assert deux_fois.status_code == 400 and par_un_client.status_code == 403
    assert len(liste) == 1 and liste[0]["client"] == "Essai Z." and "Fausse accusation" in liste[0]["signalement"]
    assert sans_motif.status_code == 400 and cache.status_code == 200 and cache.json() == {"cache": True}
    # Caché : sa note ne compte plus ; l'auteur est prévenu ; la cliente le voit encore, avec le motif
    assert page(client, dupont)["nombre_avis"] == 0
    assert any("avis sur un client est caché" in m["sujet"] for m in mails_envoyes if m["a"] == lea.email)
    assert dupont.client.get("/api/moi/avis-recus").json()[0]["cache_motif"] == "Accusation sans élément."


def test_la_note_du_client_a_cote_de_son_nom(lea, dupont, rdv_tenu, client, metiers) -> None:  # noqa: F811
    from tests.test_demandes import pelouse, publier, sur_l_accueil

    noter(lea, rdv_tenu, 4)
    demande = publier(dupont, pelouse(metiers["Coiffeur"], titre="Coupe à domicile")).json()["id"]

    carte = sur_l_accueil(client, demande)
    conversation = lea.client.get("/api/moi/conversations").json()[0]
    cote_cliente = dupont.client.get("/api/moi/conversations").json()[0]

    assert (carte["client_id"], carte["client_note"], carte["client_avis"]) == (dupont.id, 4.0, 1)
    assert conversation["cote"] == "prestataire" and (conversation["avec_note"], conversation["avec_avis"]) == (4.0, 1)
    assert cote_cliente["avec_note"] is None and cote_cliente["avec_avis"] == 0  # Léa n'a pas encore d'avis


def test_la_carte_noter_d_une_conversation(lea, dupont, rdv_tenu) -> None:  # noqa: F811
    conversation = lea.client.get("/api/moi/conversations").json()[0]["id"]

    avant = lea.client.get(f"/api/conversations/{conversation}/a-noter").json()
    noter(lea, rdv_tenu)
    apres = lea.client.get(f"/api/conversations/{conversation}/a-noter").json()
    cote_cliente = dupont.client.get(f"/api/conversations/{conversation}/a-noter").json()

    assert len(avant) == 1 and avant[0]["rendez_vous_id"] == rdv_tenu and avant[0]["deja_note"] is False
    assert apres[0]["deja_note"] is True
    assert cote_cliente[0]["deja_note"] is False  # la cliente, elle, n'a pas encore noté Léa


def test_compte_ferme_la_page_publique_disparait(lea, dupont, rdv_tenu, client, base: Session) -> None:  # noqa: F811
    noter(lea, rdv_tenu)
    base.execute(text("UPDATE compte SET ferme_le = now() WHERE id = :id"), {"id": dupont.id})
    base.commit()

    fermee = client.get(f"/api/clients/{dupont.id}/avis")
    base.execute(text("UPDATE compte SET ferme_le = NULL WHERE id = :id"), {"id": dupont.id})
    base.commit()

    assert fermee.status_code == 404 and client.get("/api/clients/999999999/avis").status_code == 404
