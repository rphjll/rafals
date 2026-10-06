"""Demandes publiées par les clients (RM-DEMANDES.md ; lot 8.3, première partie) : publier avec l'adresse et des photos,
liste de l'accueil lue par tous sans la rue ni le nom complet, limites, modifier, fermer, prolonger, expirer."""

from datetime import UTC, datetime, timedelta

from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services import demandes
from tests.test_annonces import metiers  # noqa: F401 (fixture)
from tests.test_prestataires import JPG, PDF

AUJOURD_HUI = datetime.now(reglages.FUSEAU_AFFICHAGE).date()
PESSAC = {"adresse_ligne": "8 Allée des Pins", "code_postal": "33600", "code_insee": "33318",
          "latitude": "44.8067", "longitude": "-0.6311"}


def pelouse(metier_id: int, **modifs) -> dict:
    """« Tondre ma pelouse » · Plombier (le métier d'essai) · dès que possible · chez moi, 8 allée des Pins à Pessac · 40 €."""
    donnees = {"metier_id": metier_id, "titre": "Tondre ma pelouse", "description": "200 m², terrain plat, j'ai une prise dehors.",
               "quand": "des_que_possible", "lieu": "chez_moi", "budget_centimes": 4000, **PESSAC} | modifs
    return {cle: valeur for cle, valeur in donnees.items() if valeur is not None}


def publier(compte, donnees: dict, photos: list[tuple] | None = None):
    fichiers = [("photos", (nom, contenu, type_mime)) for nom, contenu, type_mime in photos or []]
    return compte.client.post("/api/demandes", data=donnees, files=fichiers or None)


def sur_l_accueil(client, demande_id: int) -> dict | None:
    return next((d for d in client.get("/api/demandes").json() if d["id"] == demande_id), None)


def avancer(base: Session, demande_id: int, **jours) -> None:
    """Fait comme si la demande avait été publiée plus tôt : ex. avancer(base, 3, cree=40, expire=-1)."""
    base.execute(text("UPDATE demande SET cree_le = now() - make_interval(days => :c), expire_le = now() + make_interval(days => :e)"
                      " WHERE id = :id"), {"c": jours.get("cree", 0), "e": jours.get("expire", 30), "id": demande_id})
    base.commit()


# ---------- Publier ----------


def test_publier_une_demande_avec_son_adresse(fabrique_compte, metiers) -> None:
    dupont = fabrique_compte()

    reponse = publier(dupont, pelouse(metiers["Plombier"]))

    assert reponse.status_code == 201, reponse.text
    demande = reponse.json()
    assert demande["statut"] == "ouverte" and demande["ville"] == "Pessac" and demande["metier"] == "Plombier"
    assert demande["adresse_ligne"] == "8 Allée des Pins" and demande["code_postal"] == "33600"
    assert (demande["latitude"], demande["longitude"]) == (44.8067, -0.6311)
    assert demande["budget_centimes"] == 4000 and demande["a_moi"] is True
    assert [d["id"] for d in dupont.client.get("/api/moi/demandes").json()] == [demande["id"]]


def test_tout_le_monde_lit_la_demande_sans_la_rue_ni_le_nom(fabrique_compte, metiers, client) -> None:
    dupont, voisin = fabrique_compte(), fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"])).json()

    sans_compte = sur_l_accueil(client, demande["id"])
    pour_le_voisin = sur_l_accueil(voisin.client, demande["id"])

    assert sans_compte is not None and sans_compte["client"] == "Essai Z." and sans_compte["ville"] == "Pessac"
    assert "Allée des Pins" not in str(sans_compte) and "ZZTEST" not in str(sans_compte) and "latitude" not in sans_compte
    assert pour_le_voisin["a_moi"] is False and sur_l_accueil(dupont.client, demande["id"])["a_moi"] is True


def test_la_plus_recente_en_haut(fabrique_compte, metiers, client) -> None:
    dupont = fabrique_compte()
    premiere = publier(dupont, pelouse(metiers["Plombier"])).json()["id"]
    seconde = publier(dupont, pelouse(metiers["Plombier"], titre="Tailler la haie")).json()["id"]

    ordre = [d["id"] for d in client.get("/api/demandes").json()]

    assert ordre.index(seconde) < ordre.index(premiere)


def test_il_faut_une_adresse_mail_verifiee(fabrique_compte, metiers, client) -> None:
    pas_verifie = fabrique_compte(verifie=False)

    refus = publier(pas_verifie, pelouse(metiers["Plombier"]))
    sans_compte = client.post("/api/demandes", data=pelouse(metiers["Plombier"]))

    assert refus.status_code == 403 and "Vérifiez votre adresse mail" in refus.json()["detail"]
    assert sans_compte.status_code == 401


def test_textes_surveilles(fabrique_compte, metiers) -> None:
    dupont = fabrique_compte()
    plombier = metiers["Plombier"]

    telephone = publier(dupont, pelouse(plombier, description="Appelez-moi au 06 12 34 56 78 pour la pelouse."))
    mail = publier(dupont, pelouse(plombier, description="Écrivez à marie.dupont@example.com pour la pelouse."))
    injure = publier(dupont, pelouse(plombier, description="Mon voisin est un ZZINJURE, venez tondre chez moi."))
    court = publier(dupont, pelouse(plombier, titre="Aide"))
    description_courte = publier(dupont, pelouse(plombier, description="Vite."))

    assert telephone.status_code == 400 and "coordonnées" in telephone.json()["detail"]
    assert mail.status_code == 400 and "coordonnées" in mail.json()["detail"]
    assert injure.status_code == 400 and "injurieux" in injure.json()["detail"]
    assert court.status_code == 400 and "Le titre doit faire entre 5 et 80" in court.json()["detail"]
    assert description_courte.status_code == 400 and "La description doit faire entre 20 et 1000" in description_courte.json()["detail"]


def test_cinq_demandes_ouvertes_au_plus(fabrique_compte, metiers) -> None:
    dupont = fabrique_compte()
    for rang in range(reglages.DEMANDE_OUVERTES_MAX):
        assert publier(dupont, pelouse(metiers["Plombier"], titre=f"Demande numéro {rang + 1}")).status_code == 201

    sixieme = publier(dupont, pelouse(metiers["Plombier"], titre="Demande numéro 6"))
    premiere = dupont.client.get("/api/moi/demandes").json()[-1]["id"]
    assert dupont.client.post(f"/api/demandes/{premiere}/fermer").status_code == 200
    apres_fermeture = publier(dupont, pelouse(metiers["Plombier"], titre="Demande numéro 6"))

    assert sixieme.status_code == 400 and "déjà 5 demandes ouvertes" in sixieme.json()["detail"]
    assert apres_fermeture.status_code == 201


# ---------- Quand, où ----------


def test_un_jour_precis(fabrique_compte, metiers) -> None:
    dupont = fabrique_compte()
    plombier = metiers["Plombier"]
    samedi = AUJOURD_HUI + timedelta(days=4)

    sans_jour = publier(dupont, pelouse(plombier, quand="jour_precis"))
    hier = publier(dupont, pelouse(plombier, quand="jour_precis", jour=(AUJOURD_HUI - timedelta(days=1)).isoformat()))
    acceptee = publier(dupont, pelouse(plombier, quand="jour_precis", jour=samedi.isoformat()))
    jour_oublie = publier(dupont, pelouse(plombier, titre="Tailler la haie", quand="pas_presse", jour=samedi.isoformat()))

    assert sans_jour.status_code == 400 and "Indiquez le jour voulu" in sans_jour.json()["detail"]
    assert hier.status_code == 400 and "déjà passé" in hier.json()["detail"]
    assert acceptee.status_code == 201 and acceptee.json()["jour"] == samedi.isoformat()
    # Elle se ferme à la fin du jour demandé (minuit, heure de Paris), bien avant les 30 jours
    fin = datetime.fromisoformat(acceptee.json()["expire_le"]).astimezone(reglages.FUSEAU_AFFICHAGE)
    assert (fin.date(), fin.hour, fin.minute) == (samedi + timedelta(days=1), 0, 0)
    # Un jour envoyé sans « un jour précis » est ignoré
    assert jour_oublie.status_code == 201 and jour_oublie.json()["jour"] is None


def test_chez_moi_demande_la_rue_chez_le_prestataire_non(fabrique_compte, metiers) -> None:
    dupont = fabrique_compte()
    plombier = metiers["Plombier"]

    sans_rue = publier(dupont, pelouse(plombier, adresse_ligne=None))
    chez_le_prestataire = publier(dupont, pelouse(plombier, lieu="chez_prestataire", adresse_ligne=None, latitude=None, longitude=None))
    sans_ville = publier(dupont, pelouse(plombier, code_insee=None, code_postal=None))

    assert sans_rue.status_code == 400 and "adresse complète" in sans_rue.json()["detail"]
    assert chez_le_prestataire.status_code == 201 and chez_le_prestataire.json()["adresse_ligne"] is None
    assert chez_le_prestataire.json()["ville"] == "Pessac" and chez_le_prestataire.json()["latitude"] is None
    assert sans_ville.status_code == 400 and "dans la liste" in sans_ville.json()["detail"]


def test_la_ville_est_retrouvee_par_le_code_postal(fabrique_compte, metiers) -> None:
    """Le service d'adresses peut donner un code de ville inconnu de rafals (ex. un arrondissement)."""
    dupont = fabrique_compte()

    reponse = publier(dupont, pelouse(metiers["Plombier"], code_insee="99999", code_postal="33400"))

    assert reponse.status_code == 201 and reponse.json()["ville"] == "Talence" and reponse.json()["code_postal"] == "33400"


# ---------- Photos ----------


def test_photos_d_une_demande(fabrique_compte, metiers, client) -> None:
    dupont, voisin = fabrique_compte(), fabrique_compte()
    plombier = metiers["Plombier"]

    demande = publier(dupont, pelouse(plombier), [("jardin.jpg", JPG, "image/jpeg"), ("haie.jpg", JPG, "image/jpeg")]).json()
    pdf = publier(dupont, pelouse(plombier, titre="Tailler la haie"), [("plan.pdf", PDF, "application/pdf")])
    trop = publier(dupont, pelouse(plombier, titre="Tailler la haie"), [(f"p{n}.jpg", JPG, "image/jpeg") for n in range(6)])

    assert demande["nombre_photos"] == 2 and sur_l_accueil(client, demande["id"])["nombre_photos"] == 2
    photo = voisin.client.get(f"/api/demandes/{demande['id']}/photos/2")
    assert photo.status_code == 200 and photo.content == JPG and photo.headers["content-type"] == "image/jpeg"
    assert client.get(f"/api/demandes/{demande['id']}/photos/1").status_code == 401  # il faut être connecté
    assert voisin.client.get(f"/api/demandes/{demande['id']}/photos/3").status_code == 404
    assert pdf.status_code == 400 and trop.status_code == 400 and "Au plus 5 photos" in trop.json()["detail"]
    # Une demande refusée ne laisse rien derrière elle
    assert len(dupont.client.get("/api/moi/demandes").json()) == 1


# ---------- Modifier, fermer ----------


def test_modifier_sa_demande(fabrique_compte, metiers, client) -> None:
    dupont, voisin = fabrique_compte(), fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"])).json()
    nouvelle = pelouse(metiers["Électricien"], titre="Tondre et ramasser", budget_centimes=5000) | {"latitude": 44.8067, "longitude": -0.6311}

    par_un_autre = voisin.client.put(f"/api/demandes/{demande['id']}", json=nouvelle)
    modifiee = dupont.client.put(f"/api/demandes/{demande['id']}", json=nouvelle)

    assert par_un_autre.status_code == 404
    assert modifiee.status_code == 200 and modifiee.json()["titre"] == "Tondre et ramasser"
    vue = sur_l_accueil(client, demande["id"])
    assert vue["metier"] == "Électricien" and vue["budget_centimes"] == 5000


def test_fermer_sa_demande(fabrique_compte, metiers, client) -> None:
    dupont, voisin = fabrique_compte(), fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"])).json()

    par_un_autre = voisin.client.post(f"/api/demandes/{demande['id']}/fermer")
    fermee = dupont.client.post(f"/api/demandes/{demande['id']}/fermer")
    deux_fois = dupont.client.post(f"/api/demandes/{demande['id']}/fermer")
    modifier_apres = dupont.client.put(f"/api/demandes/{demande['id']}", json=pelouse(metiers["Plombier"]) | {"latitude": None, "longitude": None})

    assert par_un_autre.status_code == 404
    assert fermee.status_code == 200 and fermee.json()["statut"] == "fermee"
    assert deux_fois.status_code == 400 and modifier_apres.status_code == 400
    assert sur_l_accueil(client, demande["id"]) is None
    # Jamais effacée : elle reste dans « Mes demandes », et ses photos ne sont plus montrées aux autres
    assert dupont.client.get("/api/moi/demandes").json()[0]["statut"] == "fermee"
    assert voisin.client.get(f"/api/demandes/{demande['id']}/photos/1").status_code == 404


# ---------- Fin d'une demande ----------


def test_rappel_trois_jours_avant_puis_expiration(fabrique_compte, metiers, client, base: Session, mails_envoyes) -> None:
    dupont = fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"])).json()
    avancer(base, demande["id"], cree=28, expire=2)

    premier_passage = demandes.traiter(base, datetime.now(UTC))
    second_passage = demandes.traiter(base, datetime.now(UTC))
    base.commit()

    rappels = [m for m in mails_envoyes if m["a"] == dupont.email and "se ferme bientôt" in m["sujet"]]
    assert premier_passage[1] >= 1 and len(rappels) == 1 and "prolongez-la de 30 jours" in rappels[0]["texte"]
    assert second_passage[1] == 0  # jamais deux fois le même rappel

    avancer(base, demande["id"], cree=31, expire=-1)
    demandes.traiter(base, datetime.now(UTC))
    base.commit()

    assert dupont.client.get("/api/moi/demandes").json()[0]["statut"] == "expiree"
    assert sur_l_accueil(client, demande["id"]) is None


def test_prolonger(fabrique_compte, metiers, client, base: Session) -> None:
    dupont = fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"])).json()
    avancer(base, demande["id"], cree=31, expire=-1)
    demandes.traiter(base, datetime.now(UTC))
    base.commit()

    prolongee = dupont.client.post(f"/api/demandes/{demande['id']}/prolonger")

    assert prolongee.status_code == 200 and prolongee.json()["statut"] == "ouverte"
    reste = datetime.fromisoformat(prolongee.json()["expire_le"]) - datetime.now(UTC)
    assert timedelta(days=29) < reste <= timedelta(days=30)
    assert sur_l_accueil(client, demande["id"]) is not None
    dupont.client.post(f"/api/demandes/{demande['id']}/fermer")
    assert dupont.client.post(f"/api/demandes/{demande['id']}/prolonger").status_code == 400


def test_pas_de_rappel_pour_une_demande_courte(fabrique_compte, metiers, base: Session, mails_envoyes) -> None:
    """Publiée aujourd'hui pour après-demain : elle dure moins de 3 jours, le rappel n'aurait pas de sens."""
    dupont = fabrique_compte()
    publier(dupont, pelouse(metiers["Plombier"], quand="jour_precis", jour=(AUJOURD_HUI + timedelta(days=1)).isoformat()))

    demandes.traiter(base, datetime.now(UTC))
    base.commit()

    assert not [m for m in mails_envoyes if m["a"] == dupont.email and "se ferme bientôt" in m["sujet"]]


def test_la_demande_d_un_compte_ferme_n_est_plus_montree(fabrique_compte, metiers, client, base: Session) -> None:
    dupont = fabrique_compte()
    demande = publier(dupont, pelouse(metiers["Plombier"])).json()

    base.execute(text("UPDATE compte SET ferme_le = now() WHERE id = :id"), {"id": dupont.id})
    base.commit()

    assert sur_l_accueil(client, demande["id"]) is None
    base.execute(text("UPDATE compte SET ferme_le = NULL WHERE id = :id"), {"id": dupont.id})
    base.commit()
