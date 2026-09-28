"""Nettoie les données d'essai saisies à la main dans la VRAIE base (rafals_db).

Chaque ligne est classée :
- protégée : dans la liste PROTEGEES (vraies données) → jamais touchée ;
- marquée test : correspond à une marque (@example.com, « ZZTEST », « ZZ- ») → effacée APRÈS accord ;
- douteuse : ressemble à un essai sans être marquée → seulement signalée, JAMAIS effacée.

Lancé par nettoyer-donnees-test.bat, qui fait une sauvegarde de la base juste avant.
À compléter à chaque nouvelle table qui contient des données saisies à la main.
"""

from sqlalchemy import text

from app.db import moteur

# (table, colonne, marque de test au format SQL LIKE) — une ligne par table concernée.
# Exemple, quand la table des comptes existera : ("compte", "email", "%@example.com")
MARQUES: list[tuple[str, str, str]] = []

# Identifiants de vraies lignes à ne jamais toucher, même si elles portent une marque.
# Exemple : {"compte": [12, 45]}
PROTEGEES: dict[str, list[int]] = {}

# Ce qui fait penser à un essai sans être une marque officielle → seulement signalé
MOTS_DOUTEUX = ["%test%", "%essai%", "%zz%"]


def main() -> None:
    if not MARQUES:
        print("Aucune table à nettoyer pour l'instant : 0 donnée de test.")
        return

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

    with moteur.begin() as connexion:
        for table, _valeur, identifiant in a_effacer:
            connexion.execute(text(f"DELETE FROM {table} WHERE id = :id"), {"id": identifiant})
    print(f"{len(a_effacer)} ligne(s) effacée(s).")


if __name__ == "__main__":
    main()
