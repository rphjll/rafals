"""Limites d'un prestataire sans SIRET vérifié (RM-PRESTATAIRES.md § « Limites d'un prestataire sans SIRET »,
RM-METIERS-SANS-SIRET.md) : métiers interdits, adresse et case, 100 € par proposition, 2 rendez-vous par mois,
1 000 € sur 12 mois, propositions retirées au plafond. Avec un SIRET vérifié, aucune limite."""

from datetime import UTC, datetime, time, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import reglages
from app.services import particuliers
from tests.test_demandes import AUJOURD_HUI, pelouse, publier, sur_l_accueil
from tests.test_prestataires import devenir, id_commune, id_metier, siret_verifie

pytestmark = pytest.mark.limites_particulier  # ici, les prestataires sans SIRET ont vraiment leurs limites

PARIS = reglages.FUSEAU_AFFICHAGE


def a(jours: int, heure: int = 10) -> datetime:
    return datetime.combine(AUJOURD_HUI + timedelta(days=jours), time(heure), tzinfo=PARIS)


@pytest.fixture
def metiers(client) -> dict[str, int]:
    """Deux métiers autorisés sans SIRET, un métier qui en demande un."""
    return {nom: id_metier(client, nom) for nom in ("Promeneur de chiens", "Jardinier", "Plombier")}


@pytest.fixture
def fabrique_emma(fabrique_compte, client, metiers):
    """Emma, sans SIRET : promeneuse de chiens (principal), jardinière et plombière (secondaires), Pessac, 15 km."""

    def fabriquer(prete: bool = True):
        compte = fabrique_compte()
        reponse = devenir(compte, {
            "nom_affiche": "Emma Leroy", "metier_principal_id": metiers["Promeneur de chiens"],
            "commune_id": id_commune(client, "33600", "Pessac"), "distance_km": 15,
            "metiers_secondaires": [metiers["Jardinier"], metiers["Plombier"]],
        })
        assert reponse.status_code == 201, reponse.text
        if prete:
            preparer(compte, client)
        return compte

    return fabriquer


def preparer(compte, client) -> None:
    """Son adresse, puis la case « Mon activité est occasionnelle… »."""
    adresse = compte.client.post("/api/moi/adresse", json={"ligne": "3 rue du Moulin", "commune_id": id_commune(client, "33600", "Pessac"),
                                                           "code_postal": "33600"})
    assert adresse.status_code in (200, 201), adresse.text
    assert compte.client.post("/api/moi/prestataire/activite-occasionnelle").status_code == 200


@pytest.fixture
def fabrique_demande(fabrique_compte, metiers):
    def fabriquer(metier: str = "Promeneur de chiens", titre: str = "Promener mon chien le midi"):
        cliente = fabrique_compte()
        reponse = publier(cliente, pelouse(metiers[metier], titre=titre, description="Un labrador calme, une demi-heure autour du parc."))
        assert reponse.status_code == 201, reponse.text
        cliente.demande = reponse.json()["id"]
        return cliente

    return fabriquer


def repondre(prestataire, demande_id: int):
    return prestataire.client.post(f"/api/demandes/{demande_id}/repondre")


def proposer(prestataire, cliente, debut: datetime, prix: int = 1500):
    conversation = repondre(prestataire, cliente.demande)
    assert conversation.status_code == 201, conversation.text
    return prestataire.client.post(f"/api/conversations/{conversation.json()['conversation_id']}/propositions", json={
        "prix_centimes": prix, "debut": debut.isoformat(), "duree_minutes": 30, "demande_id": cliente.demande, "paiement_especes": True})


def accepter(cliente, proposition_id: int):
    return cliente.client.post(f"/api/propositions/{proposition_id}/accepter", json={"mode_paiement": "especes"})


def rendez_vous_passe(base: Session, rdv_id: int, il_y_a_jours: int) -> None:
    """Fait comme si ce rendez-vous avait eu lieu il y a quelques jours."""
    base.execute(text("UPDATE rendez_vous SET debut = now() - make_interval(days => :j), fin = now() - make_interval(days => :j)"
                      " + interval '30 minutes' WHERE id = :id"), {"j": il_y_a_jours, "id": rdv_id})
    base.commit()


def limites(compte) -> dict:
    return compte.client.get("/api/moi/prestataire/limites").json()


# ---------- Règle 1 : les métiers ----------


def test_metiers_ranges_par_la_liste(base: Session) -> None:
    obligatoire = dict(base.execute(text("SELECT nom, siret_obligatoire FROM metier")).all())

    assert obligatoire["Plombier"] and obligatoire["Coiffeur / Coiffeuse"] and obligatoire["Coach sportif"] and obligatoire["Autre"]
    assert not obligatoire["Promeneur de chiens"] and not obligatoire["Jardinier"] and not obligatoire["Repassage"]
    assert not obligatoire["Garde d'enfants / Baby-sitting"] and not obligatoire["Montage de meubles"]
    assert sum(1 for oui in obligatoire.values() if not oui) == 50


def test_un_metier_ajoute_plus_tard_demande_un_siret(base: Session) -> None:
    categorie = base.execute(text("SELECT id FROM categorie_metier LIMIT 1")).scalar_one()
    base.execute(text("INSERT INTO metier (categorie_id, code, nom) VALUES (:c, 'zztest-metier-nouveau', 'ZZTEST Métier nouveau')"), {"c": categorie})
    obligatoire = base.execute(text("SELECT siret_obligatoire FROM metier WHERE code = 'zztest-metier-nouveau'")).scalar_one()
    base.rollback()

    assert obligatoire is True


def test_sans_siret_pas_de_reponse_a_un_metier_interdit(fabrique_emma, fabrique_demande, base: Session) -> None:
    emma = fabrique_emma()
    chien, fuite = fabrique_demande(), fabrique_demande("Plombier", "Fuite sous l'évier")

    carte_chien, carte_fuite = sur_l_accueil(emma.client, chien.demande), sur_l_accueil(emma.client, fuite.demande)
    refus = repondre(emma, fuite.demande)

    assert carte_chien["peut_repondre"] is True and carte_chien["raison_verrou"] is None
    assert carte_fuite["peut_repondre"] is False and "« Plombier » demande un SIRET" in carte_fuite["raison_verrou"]
    assert refus.status_code == 403 and "demande un SIRET" in refus.json()["detail"]
    assert repondre(emma, chien.demande).status_code == 201
    # Les deux restent dans « Demandes près de chez moi » : la fuite avec son bouton verrouillé
    pres = {d["id"]: d for d in emma.client.get("/api/moi/prestataire/demandes").json()}
    assert chien.demande in pres and pres[fuite.demande]["raison_verrou"]
    # SIRET vérifié : plus aucune limite
    siret_verifie(base, emma)
    assert sur_l_accueil(emma.client, fuite.demande)["peut_repondre"] is True and repondre(emma, fuite.demande).status_code == 201


# ---------- Règle 7 : l'adresse et la case ----------


def test_adresse_et_case_avant_la_premiere_reponse(fabrique_emma, fabrique_demande, client) -> None:
    emma = fabrique_emma(prete=False)
    chien = fabrique_demande()

    avant = limites(emma)
    carte = sur_l_accueil(emma.client, chien.demande)
    refus = repondre(emma, chien.demande)
    preparer(emma, client)
    apres = limites(emma)

    assert avant["particulier"] is True and avant["adresse_remplie"] is False and avant["case_cochee_le"] is None
    assert avant["etiquette"] == "Particulier, non professionnel" and "Pas de facture" in avant["avertissement"]
    assert carte["peut_repondre"] is False and "Ajoutez votre adresse" in carte["raison_verrou"]
    assert refus.status_code == 403 and "Ajoutez votre adresse" in refus.json()["detail"]
    assert apres["adresse_remplie"] is True and apres["case_cochee_le"] is not None
    assert repondre(emma, chien.demande).status_code == 201
    # La date de la case est gardée : cocher une 2e fois ne la change pas
    assert emma.client.post("/api/moi/prestataire/activite-occasionnelle").json()["case_cochee_le"] == apres["case_cochee_le"]


# ---------- Règle 2 : 100 € par proposition ----------


def test_cent_euros_au_plus_par_proposition(fabrique_emma, fabrique_demande, base: Session) -> None:
    emma = fabrique_emma()
    garage = fabrique_demande("Jardinier", "Débarrasser le jardin")

    trop = proposer(emma, garage, a(3), prix=25000)
    juste = proposer(emma, garage, a(3), prix=10000)

    assert trop.status_code == 400 and "ne peut pas dépasser 100,00 €" in trop.json()["detail"]
    assert juste.status_code == 201 and juste.json()["particulier"] is True and juste.json()["modes_de_paiement"] == ["especes"]
    siret_verifie(base, emma)
    assert proposer(emma, garage, a(4), prix=25000).status_code == 201


# ---------- Règle 3 : 2 rendez-vous par mois ----------


def test_deux_rendez_vous_par_mois(fabrique_emma, fabrique_demande, base: Session) -> None:
    """Autant de propositions qu'elle veut ; bloquée quand 2 sont acceptées pour le même mois (le jour du rendez-vous)."""
    emma = fabrique_emma()
    dans_ce_mois = [fabrique_demande(titre=f"Promener mon chien n° {n}") for n in (1, 2, 3)]
    mois_suivant = fabrique_demande(titre="Promener mon chien en fin de mois")
    # Trois jours du même mois, tous à venir : le mois d'après-demain, à partir de son 20
    reference = AUJOURD_HUI + timedelta(days=40)
    jour = lambda n: datetime.combine(reference.replace(day=20 + n), time(12), tzinfo=PARIS)  # noqa: E731
    apres = datetime.combine((reference.replace(day=28) + timedelta(days=10)).replace(day=5), time(12), tzinfo=PARIS)
    propositions = [proposer(emma, cliente, jour(n)).json()["id"] for n, cliente in enumerate(dans_ce_mois)]
    autre_mois = proposer(emma, mois_suivant, apres).json()["id"]

    premier, deuxieme = accepter(dans_ce_mois[0], propositions[0]), accepter(dans_ce_mois[1], propositions[1])
    troisieme = accepter(dans_ce_mois[2], propositions[2])

    assert premier.status_code == 201 and deuxieme.status_code == 201
    assert troisieme.status_code == 400 and "limite du mois (2 rendez-vous sans SIRET)" in troisieme.json()["detail"]
    assert accepter(mois_suivant, autre_mois).status_code == 201  # un autre mois : accepté
    # Un rendez-vous annulé ne compte plus : la 3e peut alors être acceptée
    annule = emma.client.post(f"/api/moi/prestataire/rendez-vous/{premier.json()['rendez_vous_id']}/annuler", json={"motif": "Je suis malade."})
    assert annule.status_code == 200, annule.text
    assert accepter(dans_ce_mois[2], propositions[2]).status_code == 201


# ---------- Règle 4 : 1 000 € sur 12 mois ----------


def test_total_des_12_mois_et_propositions_retirees(fabrique_emma, fabrique_demande, base: Session, mails_envoyes, monkeypatch) -> None:
    monkeypatch.setattr(reglages, "PARTICULIER_TOTAL_CENTIMES", 3000)  # 1 000 € dans la règle ; 30 € ici
    emma = fabrique_emma()
    clientes = [fabrique_demande(titre=f"Promener mon chien n° {n}") for n in (1, 2, 3, 4)]
    acceptees = [accepter(c, proposer(emma, c, a(40 + 31 * n)).json()["id"]).json()["rendez_vous_id"] for n, c in enumerate(clientes[:3])]
    en_attente = proposer(emma, clientes[3], a(200))
    assert en_attente.status_code == 201

    # Rien n'a encore eu lieu : 0 € ; un rendez-vous à venir ne compte pas
    assert limites(emma)["total_12_mois_centimes"] == 0 and limites(emma)["plafond_atteint"] is False
    rendez_vous_passe(base, acceptees[0], 10)   # 15 € il y a 10 jours
    rendez_vous_passe(base, acceptees[1], 400)  # 15 € il y a plus de 12 mois : ne compte pas
    assert limites(emma)["total_12_mois_centimes"] == 1500
    assert particuliers.retirer_au_plafond(base, datetime.now(UTC)) == 0
    rendez_vous_passe(base, acceptees[2], 5)    # 15 € de plus : 30 €, le plafond
    etat = limites(emma)
    retirees = particuliers.retirer_au_plafond(base, datetime.now(UTC))
    base.commit()

    assert etat["total_12_mois_centimes"] == 3000 and etat["plafond_atteint"] is True
    assert retirees == 1 and particuliers.retirer_au_plafond(base, datetime.now(UTC)) == 0
    conversation = en_attente.json()["conversation_id"]
    vues = clientes[3].client.get(f"/api/conversations/{conversation}/propositions").json()
    assert vues[0]["statut"] == "retiree"
    recus = [m for m in mails_envoyes if m["a"] == emma.email and "limite des particuliers" in m["sujet"]]
    assert len(recus) == 1 and "Vos rendez-vous déjà confirmés restent" in recus[0]["texte"]
    # Elle ne peut plus répondre ni proposer ; la cliente ne peut plus accepter
    nouvelle = fabrique_demande(titre="Promener mon chien demain")
    carte = sur_l_accueil(emma.client, nouvelle.demande)
    assert carte["peut_repondre"] is False and "limite des particuliers" in carte["raison_verrou"]
    assert repondre(emma, nouvelle.demande).status_code == 403
    assert accepter(clientes[3], en_attente.json()["id"]).status_code == 400
    # Avec un SIRET vérifié, tout repart
    siret_verifie(base, emma)
    assert repondre(emma, nouvelle.demande).status_code == 201


def test_un_rendez_vous_avec_absence_ne_compte_pas(fabrique_emma, fabrique_demande, base: Session) -> None:
    emma = fabrique_emma()
    cliente = fabrique_demande()
    rdv = accepter(cliente, proposer(emma, cliente, a(3)).json()["id"]).json()["rendez_vous_id"]
    rendez_vous_passe(base, rdv, 2)
    assert limites(emma)["total_12_mois_centimes"] == 1500

    base.execute(text("UPDATE rendez_vous SET absent = 'client', absence_signalee_le = now() WHERE id = :id"), {"id": rdv})
    base.commit()

    assert limites(emma)["total_12_mois_centimes"] == 0


# ---------- Avec un SIRET vérifié : aucune limite ----------


def test_avec_un_siret_verifie_aucune_limite(fabrique_emma, fabrique_demande, base: Session) -> None:
    emma = fabrique_emma()
    siret_verifie(base, emma)
    fuite = fabrique_demande("Plombier", "Fuite sous l'évier")

    proposition = proposer(emma, fuite, a(3), prix=45000)

    assert limites(emma)["particulier"] is False
    assert proposition.status_code == 201 and proposition.json()["particulier"] is False
    assert accepter(fuite, proposition.json()["id"]).status_code == 201
