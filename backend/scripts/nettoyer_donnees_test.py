"""Nettoie les données d'essai saisies à la main dans la VRAIE base (rafals_db).

Chaque ligne est classée :
- protégée : dans la liste PROTEGEES (vraies données) → jamais touchée ;
- marquée test : correspond à une marque (@example.com, « ZZTEST », « ZZ- ») → effacée APRÈS accord ;
- douteuse : ressemble à un essai sans être marquée → seulement signalée, JAMAIS effacée.

Lancé par nettoyer-donnees-test.bat, qui fait une sauvegarde de la base juste avant.
À compléter à chaque nouvelle table qui contient des données saisies à la main.

L'effacement se fait avec le compte ADMINISTRATEUR de la base : c'est la seule exception à
« on n'efface jamais le journal » (les lignes du journal d'un compte d'essai sont elles-mêmes des essais).
"""

import os

from sqlalchemy import URL, create_engine, text

from app import config
from app.db import moteur
from app.services import stockage

# (table, colonne, marque de test au format SQL LIKE) — une ligne par table concernée.
MARQUES: list[tuple[str, str, str]] = [
    ("compte", "email", "%@example.com"),
    ("metier", "nom", "ZZTEST %"),
]

# Lignes rattachées à effacer AVANT la ligne principale, dans cet ordre (la base refuse sinon).
RATTACHEES: dict[str, list[str]] = {
    "compte": [
        "DELETE FROM journal_action WHERE auteur_id = :id OR (table_cible = 'compte' AND ligne_id = :id)"
        " OR (table_cible = 'dossier_creation' AND ligne_id IN (SELECT id FROM dossier_creation WHERE compte_id = :id))"
        " OR (table_cible = 'accord_parental' AND ligne_id IN (SELECT id FROM accord_parental WHERE compte_id = :id))"
        " OR (table_cible = 'proposition_metier' AND ligne_id IN (SELECT id FROM proposition_metier WHERE propose_par_id = :id))"
        " OR (table_cible = 'prestataire' AND ligne_id IN (SELECT id FROM prestataire WHERE compte_id = :id))"
        " OR (table_cible = 'annonce' AND ligne_id IN (SELECT a.id FROM annonce a JOIN prestataire p ON p.id = a.prestataire_id"
        " WHERE p.compte_id = :id))"
        " OR (table_cible = 'local' AND ligne_id IN (SELECT l.id FROM local l JOIN prestataire p ON p.id = l.prestataire_id"
        " WHERE p.compte_id = :id))"
        " OR (table_cible = 'blocage' AND ligne_id IN (SELECT b.id FROM blocage b JOIN prestataire p ON p.id = b.prestataire_id"
        " WHERE p.compte_id = :id))"
        " OR (table_cible = 'ouverture' AND ligne_id IN (SELECT o.id FROM ouverture o JOIN prestataire p ON p.id = o.prestataire_id"
        " WHERE p.compte_id = :id))"
        " OR (table_cible = 'conversation' AND ligne_id IN (SELECT c.id FROM conversation c WHERE c.client_id = :id OR c.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))"
        " OR (table_cible = 'rendez_vous' AND ligne_id IN (SELECT r.id FROM rendez_vous r WHERE r.client_id = :id"
        " OR r.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))"
        " OR (table_cible = 'avis' AND ligne_id IN (SELECT a.id FROM avis a WHERE a.client_id = :id"
        " OR a.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))"
        " OR (table_cible = 'mot_interdit' AND ligne_id IN (SELECT m.id FROM mot_interdit m WHERE m.ajoute_par_id = :id))"
        " OR (table_cible = 'paiement' AND ligne_id IN (SELECT pa.id FROM paiement pa JOIN rendez_vous r ON r.id = pa.rendez_vous_id"
        " WHERE r.client_id = :id OR r.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))"
        " OR (table_cible = 'paiement' AND ligne_id IN (SELECT pa.id FROM paiement pa WHERE pa.devis_id IN (SELECT v.id FROM devis v WHERE v.demande_devis_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))))"
        " OR (table_cible = 'facture' AND ligne_id IN (SELECT f.id FROM facture f WHERE f.client_id = :id OR f.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))"
        " OR (table_cible = 'demande_devis' AND ligne_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))"
        " OR (table_cible = 'devis' AND ligne_id IN (SELECT v.id FROM devis v WHERE v.demande_devis_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))))",
        # Dossiers de création d'auto-entreprise d'essai (lot 7.1) : papiers, puis dossiers
        "DELETE FROM piece_dossier WHERE dossier_id IN (SELECT id FROM dossier_creation WHERE compte_id = :id)",
        "DELETE FROM dossier_creation WHERE compte_id = :id",
        "DELETE FROM avis WHERE client_id = :id OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM mot_interdit WHERE ajoute_par_id = :id",
        # Signalements et rappels URSSAF d'essai (lot 6.3)
        "DELETE FROM signalement WHERE auteur_id = :id OR traite_par_id = :id OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)"
        " OR conversation_id IN (SELECT c.id FROM conversation c WHERE c.client_id = :id OR c.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        # Messagerie (lot 8.1) : les photos, les messages, puis les conversations du compte
        "DELETE FROM photo_message WHERE message_id IN (SELECT m.id FROM message m WHERE m.auteur_id = :id OR m.conversation_id IN (SELECT c.id FROM conversation c WHERE c.client_id = :id OR c.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))",
        "DELETE FROM message WHERE auteur_id = :id OR conversation_id IN (SELECT c.id FROM conversation c WHERE c.client_id = :id OR c.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM conversation WHERE bloquee_par_id = :id OR id IN (SELECT c.id FROM conversation c WHERE c.client_id = :id OR c.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM rappel_declaration WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        # Déclarations URSSAF et accords d'essai (lot 7.3) : déclarations, puis accords
        "DELETE FROM declaration_urssaf WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM mandat_urssaf WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        # Factures et avoirs d'essai (lot 5.5), comme client ou comme prestataire : lignes, avoirs, puis factures
        "DELETE FROM ligne_facture WHERE facture_id IN (SELECT f.id FROM facture f WHERE f.client_id = :id OR f.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM facture WHERE avoir_de_id IS NOT NULL AND (client_id = :id OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM facture WHERE client_id = :id OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        # Demandes de devis et devis (lot 5.3), comme client ou comme prestataire : paiements, lignes, devis, photos, demandes
        "DELETE FROM paiement WHERE devis_id IN (SELECT v.id FROM devis v WHERE v.demande_devis_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))",
        "DELETE FROM ligne_devis WHERE devis_id IN (SELECT v.id FROM devis v WHERE v.demande_devis_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)))",
        "DELETE FROM devis WHERE demande_devis_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM photo_demande WHERE demande_devis_id IN (SELECT d.id FROM demande_devis d WHERE d.client_id = :id OR d.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM demande_devis WHERE client_id = :id OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        # Paiements par carte de ses rendez-vous (lot 5.1), avant les rendez-vous
        "DELETE FROM paiement WHERE rendez_vous_id IN (SELECT r.id FROM rendez_vous r WHERE r.client_id = :id"
        " OR r.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        # Rendez-vous du compte (comme client ou comme prestataire) : d'abord les liens « déplacé en », puis les lignes
        "UPDATE rendez_vous SET remplace_id = NULL WHERE client_id = :id"
        " OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)"
        " OR remplace_id IN (SELECT r.id FROM rendez_vous r WHERE r.client_id = :id"
        " OR r.prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id))",
        "DELETE FROM rendez_vous WHERE client_id = :id OR prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM proposition_metier WHERE propose_par_id = :id",
        "DELETE FROM photo_annonce WHERE annonce_id IN (SELECT a.id FROM annonce a JOIN prestataire p ON p.id = a.prestataire_id"
        " WHERE p.compte_id = :id)",
        "DELETE FROM annonce WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM local WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM plage_horaire WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM blocage WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM ouverture WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM metier_secondaire WHERE prestataire_id IN (SELECT id FROM prestataire WHERE compte_id = :id)",
        "DELETE FROM prestataire WHERE compte_id = :id",
        "DELETE FROM accord_parental WHERE compte_id = :id",
        "DELETE FROM fichier WHERE depose_par_id = :id",
        "DELETE FROM adresse WHERE compte_id = :id",
        "DELETE FROM session WHERE compte_id = :id",
        "DELETE FROM jeton_mail WHERE compte_id = :id",
    ],
    "metier": [
        "DELETE FROM journal_action WHERE table_cible = 'metier' AND ligne_id = :id",
        "DELETE FROM proposition_metier WHERE metier_retenu_id = :id",
    ],
}

# Fichiers rangés dans le stockage, à retirer aussi : table → requête qui donne leurs clés
FICHIERS_RATTACHES: dict[str, str] = {
    "compte": "SELECT cle_stockage FROM fichier WHERE depose_par_id = :id",
}

# Identifiants de vraies lignes à ne jamais toucher, même si elles portent une marque.
# Exemple : {"compte": [12, 45]}
PROTEGEES: dict[str, list[int]] = {}

# Ce qui fait penser à un essai sans être une marque officielle → seulement signalé
MOTS_DOUTEUX = ["%test%", "%essai%", "%zz%"]


def moteur_administrateur():
    return create_engine(
        URL.create(
            "postgresql+psycopg",
            username=os.environ["POSTGRES_USER"],
            password=os.environ["POSTGRES_PASSWORD"],
            host=config.DB_HOTE,
            port=config.DB_PORT,
            database=config.DB_NOM,
        )
    )


def main() -> None:
    a_effacer: list[tuple[str, str, int]] = []
    with moteur.connect() as connexion:
        for table, colonne, marque in MARQUES:
            protegees = PROTEGEES.get(table, [])
            lignes = connexion.execute(
                text(f"SELECT id, {colonne} FROM {table} WHERE {colonne} LIKE :marque"),
                {"marque": marque},
            ).all()
            for identifiant, valeur in lignes:
                if identifiant not in protegees:
                    a_effacer.append((table, valeur, identifiant))

            douteuses = connexion.execute(
                text(
                    f"SELECT id, {colonne} FROM {table} "
                    f"WHERE {colonne} NOT LIKE :marque AND ({' OR '.join(f'{colonne} ILIKE :d{i}' for i in range(len(MOTS_DOUTEUX)))})"
                ),
                {"marque": marque, **{f"d{i}": mot for i, mot in enumerate(MOTS_DOUTEUX)}},
            ).all()
            for identifiant, valeur in douteuses:
                print(f"  DOUTEUX (non touché) : {table} n° {identifiant} « {valeur} »")

    if not a_effacer:
        print("Aucune donnée de test marquée : rien à effacer.")
        return

    print(f"{len(a_effacer)} ligne(s) de test marquée(s) :")
    for table, valeur, identifiant in a_effacer:
        print(f"  {table} n° {identifiant} « {valeur} »")
    if input("Tape OUI (en majuscules) pour les effacer : ").strip() != "OUI":
        print("Annulé : rien n'a été effacé.")
        return

    cles_a_retirer: list[str] = []
    with moteur_administrateur().begin() as connexion:
        for table, _valeur, identifiant in a_effacer:
            if table in FICHIERS_RATTACHES:
                cles_a_retirer += connexion.execute(text(FICHIERS_RATTACHES[table]), {"id": identifiant}).scalars().all()
            for requete in RATTACHEES.get(table, []):
                connexion.execute(text(requete), {"id": identifiant})
            connexion.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": identifiant})
    for cle in cles_a_retirer:
        stockage.supprimer(cle)
    print(f"{len(a_effacer)} ligne(s) effacée(s), {len(cles_a_retirer)} fichier(s) retiré(s) du stockage.")


if __name__ == "__main__":
    main()
