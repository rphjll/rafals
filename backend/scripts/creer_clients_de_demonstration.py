"""Crée un prestataire d'essai et trois clients d'essai dans la VRAIE base (rafals_db), pour regarder « Mes clients »
et les chiffres de « Mon activité » avec des données (demande de Raphael du 07/10/2026).

Tout passe par les adresses du serveur, comme si quatre personnes utilisaient le site : les règles sont respectées.
Tout est marqué : les quatre comptes ont une adresse en @example.com, le prestataire s'appelle « ZZTEST … ».
Depuis le lot 9.4 (17/10/2026, plus d'annonces), un rendez-vous naît d'une proposition acceptée, comme sur le site.
Mot de passe des quatre comptes : 123. nettoyer-donnees-test.bat efface le tout.

Les seules écritures directes dans la base portent sur les lignes créées ici : adresse mail marquée « vérifiée »,
mot de passe « 123 » (le site en exige 10 caractères), SIRET d'essai marqué « vérifié », et deux rendez-vous reculés
dans le passé pour qu'ils comptent comme « faits ».

Lancer :  docker compose exec backend python -m scripts.creer_clients_de_demonstration
"""

import sys
from datetime import date, datetime, time, timedelta

from fastapi.testclient import TestClient
from sqlalchemy import text

from app import reglages
from app.db import moteur
from app.main import app
from app.services import securite

PARIS = reglages.FUSEAU_AFFICHAGE
MOT_DE_PASSE = "123"
MOT_DE_PASSE_LONG = "MaisonBleue44"  # seulement le temps de créer le compte
KARIM = "zztest.karim@example.com"
CLIENTS = {
    "julie": ("Julie", "Martin", "zztest.julie@example.com", "0612345678"),
    "hugo": ("Hugo", "Petit", "zztest.hugo@example.com", "0623456789"),
    "nadia": ("Nadia", "Benali", "zztest.nadia@example.com", "0634567890"),
}


def sql(requete: str, **valeurs) -> None:
    with moteur.begin() as connexion:
        connexion.execute(text(requete), valeurs)


def ok(reponse, attendu: tuple[int, ...] = (200, 201)):
    if reponse.status_code not in attendu:
        sys.exit(f"ARRET : {reponse.request.method} {reponse.request.url.path} a repondu {reponse.status_code} : {reponse.text}")
    return reponse.json()


def creer_compte(prenom: str, nom: str, email: str, telephone: str) -> tuple[TestClient, int]:
    """Un compte d'essai, adresse vérifiée, connecté, mot de passe « 123 »."""
    client = TestClient(app)
    identifiant = ok(client.post("/api/comptes", json={
        "email": email, "mot_de_passe": MOT_DE_PASSE_LONG, "prenom": prenom, "nom": nom, "telephone": telephone,
        "date_naissance": date(1990, 1, 1).isoformat()}))["id"]
    sql("UPDATE compte SET email_verifie_le = now(), mot_de_passe_hache = :h WHERE id = :id AND email = :e",
        h=securite.hacher_mot_de_passe(MOT_DE_PASSE), id=identifiant, e=email)
    ok(client.post("/api/connexion", json={"email": email, "mot_de_passe": MOT_DE_PASSE}))
    return client, identifiant


def reculer(rdv_id: int, jours: int) -> None:
    """Comme si le rendez-vous avait eu lieu il y a « jours » jours."""
    sql("UPDATE rendez_vous SET debut = now() - make_interval(days => :j, hours => 2),"
        " fin = now() - make_interval(days => :j, hours => 2) + (fin - debut) WHERE id = :id", j=jours, id=rdv_id)


def main() -> None:
    with moteur.connect() as connexion:
        deja = connexion.scalar(text("SELECT count(*) FROM compte WHERE email = ANY(:e)"),
                                {"e": [KARIM, *(c[2] for c in CLIENTS.values())]})
    if deja:
        sys.exit("ARRET : ces comptes d'essai existent deja. Lance nettoyer-donnees-test.bat avant de recommencer.")

    visiteur = TestClient(app)
    metier = next(m["id"] for m in ok(visiteur.get("/api/metiers/recherche", params={"q": "Électricien"})) if m["nom"] == "Électricien")
    pessac = next(c["id"] for c in ok(visiteur.get("/api/communes/recherche", params={"q": "33600"})) if c["nom"] == "Pessac")

    # --- Le prestataire d'essai : électricien à Pessac, ouvert tous les jours de 8 h à 20 h
    karim, karim_id = creer_compte("Karim", "Benali", KARIM, "0601020304")
    ok(karim.post("/api/moi/prestataire", json={"nom_affiche": "ZZTEST Karim Benali", "metier_principal_id": metier,
                                                "commune_id": pessac, "distance_km": 15, "metiers_secondaires": []}))
    sql("UPDATE prestataire SET siret = '44306184100047', siret_statut = 'verifie' WHERE compte_id = :id", id=karim_id)
    ok(karim.post("/api/moi/agenda/semaine", json={"plages": [{"jour_semaine": j, "debut": "08:00", "fin": "20:00"} for j in range(1, 8)]}))
    karim_prestataire = ok(karim.get("/api/moi/prestataire"))["id"]

    # --- Les trois clients, avec leur adresse à Pessac (les rendez-vous ont lieu chez le client)
    comptes = {}
    for cle, (prenom, nom, email, telephone) in CLIENTS.items():
        client, _ = creer_compte(prenom, nom, email, telephone)
        ok(client.post("/api/moi/adresse", json={"ligne": "8 allée des Pins", "commune_id": pessac, "code_postal": "33600"}))
        comptes[cle] = client

    jour = datetime.now(PARIS).date() + timedelta(days=8)

    def reserver(client: TestClient, heure: int) -> int:
        """Le client écrit à Karim, Karim propose « ZZTEST Pose d'une prise » à 50 €, le client accepte en espèces."""
        conversation = ok(client.post("/api/conversations", json={"prestataire_id": karim_prestataire}))["id"]
        proposition = ok(karim.post(f"/api/conversations/{conversation}/propositions", json={
            "prix_centimes": 5000, "debut": datetime.combine(jour, time(heure), tzinfo=PARIS).isoformat(),
            "duree_minutes": 60, "paiement_especes": True, "metier_id": metier, "lieu": "chez_client"}))["id"]
        return ok(client.post(f"/api/propositions/{proposition}/accepter", json={"mode_paiement": "especes"}))["rendez_vous_id"]

    def devis(client: TestClient, texte: str) -> None:
        demande = ok(client.post("/api/devis/demandes", json={"prestataire_id": karim_prestataire, "metier_id": metier,
                                                              "texte": texte}))["id"]
        ok(karim.post(f"/api/moi/prestataire/demandes-devis/{demande}/devis", json={
            "lignes": [{"libelle": "Tableau 2 rangées", "quantite_centiemes": 100, "prix_unitaire_centimes": 18000},
                       {"libelle": "Main-d'œuvre", "quantite_centiemes": 300, "prix_unitaire_centimes": 4500}],
            "arrhes_pourcent": 30, "travaux_debut": (jour + timedelta(days=12)).isoformat(),
            "travaux_fin": (jour + timedelta(days=12)).isoformat(), "valable_jusqu_au": (jour + timedelta(days=22)).isoformat()}))

    def paye(rdv_id: int, jours: int) -> None:
        reculer(rdv_id, 1)
        ok(karim.post(f"/api/moi/prestataire/rendez-vous/{rdv_id}/paye", json={"moyen": "especes"}))
        reculer(rdv_id, jours)

    # Julie : un rendez-vous fait et payé il y a 5 jours, un rendez-vous à venir, un devis en attente
    paye(reserver(comptes["julie"], 9), 5)
    reserver(comptes["julie"], 11)
    devis(comptes["julie"], "Remplacer mon vieux tableau électrique, maison de 90 m².")
    # Hugo : un seul rendez-vous, payé, il y a 130 jours (plus de 3 mois : nom court, téléphone caché)
    paye(reserver(comptes["hugo"], 14), 130)
    # Nadia : seulement un devis, pas encore de rendez-vous
    devis(comptes["nadia"], "Mettre aux normes le tableau d'un appartement de 45 m².")

    liste = ok(karim.get("/api/moi/prestataire/clients"))
    print(f"\nFAIT. « Mes clients » de {KARIM} :")
    for c in liste:
        print(f"  - {c['nom']} | {c['rendez_vous']} rendez-vous | {c['devis']} devis ({c['devis_en_attente']} en attente)"
              f" | {c['paye_centimes'] / 100:.2f} EUR | tel. {c['telephone']}")
    print("Chiffres :", ok(karim.get("/api/moi/activite"))["prestataire"])
    print(f"\nPour regarder : se connecter avec {KARIM} / {MOT_DE_PASSE}, puis « Mon activite » > « Mes clients ».")
    print("Pour tout effacer : nettoyer-donnees-test.bat")


def chez_un_vrai_prestataire(prestataire_id: int) -> None:
    """Met les trois clients d'essai (déjà créés par main) dans « Mes clients » d'un vrai prestataire : chacun lui
    écrit, reçoit une proposition faite en son nom et l'accepte en espèces → un rendez-vous confirmé.
    Aucune facture n'est créée à son nom. Tout est rattaché aux comptes d'essai : le nettoyage l'efface avec eux.
    Ex. python -m scripts.creer_clients_de_demonstration --prestataire 14"""
    from sqlalchemy.orm import Session

    from app.modeles.prestataires import Prestataire
    from app.services import propositions

    jour = datetime.now(PARIS).date() + timedelta(days=9)

    def rendez_vous(cle: str, heure: int, prix: int) -> int:
        client = TestClient(app)
        ok(client.post("/api/connexion", json={"email": CLIENTS[cle][2], "mot_de_passe": MOT_DE_PASSE}))
        conversation = ok(client.post("/api/conversations", json={"prestataire_id": prestataire_id}))["id"]
        with Session(moteur) as db:
            prestataire = db.get_one(Prestataire, prestataire_id)
            proposition = propositions.proposer(db, prestataire, conversation, propositions.Saisie(
                prix_centimes=prix, debut=datetime.combine(jour, time(heure), tzinfo=PARIS), duree_minutes=60,
                metier_id=prestataire.metier_principal_id, lieu="chez_client"), datetime.now(PARIS))
            db.commit()
            proposition_id = proposition.id
        return ok(client.post(f"/api/propositions/{proposition_id}/accepter", json={"mode_paiement": "especes"}))["rendez_vous_id"]

    reculer(rendez_vous("julie", 9, 5000), 5)  # Julie : un rendez-vous fait il y a 5 jours…
    rendez_vous("julie", 11, 3500)  # … et un à venir
    reculer(rendez_vous("hugo", 14, 4000), 130)  # Hugo : il y a plus de 3 mois → nom court, téléphone caché
    rendez_vous("nadia", 16, 6000)  # Nadia : un rendez-vous à venir
    with Session(moteur) as db:
        from app.services import activite

        print(f"FAIT. « Mes clients » du prestataire n° {prestataire_id} :")
        for c in activite.clients_de(db, db.get_one(Prestataire, prestataire_id), datetime.now(PARIS)):
            print(f"  - {c.nom} | {c.rendez_vous} rendez-vous | {c.paye_centimes / 100:.2f} EUR | tel. {c.telephone}")


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--prestataire":
        chez_un_vrai_prestataire(int(sys.argv[2]))
    else:
        main()
