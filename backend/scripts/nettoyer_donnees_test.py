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
        " OR (table_cible = 'accord_parental' AND ligne_id IN (SELECT id FROM accord_parental WHERE compte_id = :id))"
        " OR (table_cible = 'proposition_metier' AND ligne_id IN (SELECT id FROM proposition_metier WHERE propose_par_id = :id))",
        "DELETE FROM proposition_metier WHERE propose_par_id = :id",
        "DELETE FROM accord_parental WHERE compte_id = :id",
        "DELETE FROM fichier WHERE depose_par_id = :id",
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
