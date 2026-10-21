# rafals — S'abonner à un prestataire

> Demande de Raphael du 21/10/2026, mot pour mot : « on vas ajouter un système d'abonnement donc dans trouver un prestataire a chaques prestataires on peut s'abonner et que ca apparaise a un endroit comme sur les réseaux un peut ».
> Réponses de Raphael le 21/10/2026 : une liste « Mes abonnements » + des notifications choisies (« bah la liste et dans les notifs on peut choisir quoi activer comme notifs ») ; 3 notifications ; choix **pour chaque prestataire** ; nombre d'abonnés **visible par tous**.
> Données : table `ABONNEMENT` (MLD `.doc/mld/MLD-abonnement.html`, validé le 21/10/2026 ; `db/schema_v31.sql`). Code : `backend/app/services/abonnements.py`. Tests : `backend/tests/test_abonnements.py`.

## S'abonner
1. Il faut être connecté. Un compte suit **une seule fois** le même prestataire (la base refuse un doublon).
2. On ne suit qu'un prestataire visible (activité active). Un prestataire ne peut pas s'abonner à lui-même.
3. Au moment de l'abonnement, les 3 notifications sont **cochées**.
4. Se désabonner efface la ligne, même si le prestataire est en pause, bloqué ou arrêté.
5. Compte fermé : ses abonnements sont effacés (il ne compte plus dans les abonnés).

## Le nombre d'abonnés
« 12 abonnés » sur la carte de « Trouver un prestataire » et sur la fiche du prestataire, visible par tous, même sans compte. Il n'est rangé nulle part : il est compté à chaque affichage. **Personne ne voit qui sont les abonnés**, pas même le prestataire.

## Les 3 notifications (sur l'appareil, comme les messages ; jamais de mail)
Chacune part seulement aux abonnés qui l'ont cochée pour ce prestataire, et seulement si son profil est visible. Un clic ouvre sa fiche.

| Notification | Quand | Exemple |
|---|---|---|
| **Créneau libre** | un client annule un rendez-vous à venir ; le prestataire retire une fermeture qui n'est pas finie ; il ouvre des heures en plus | « Karim Benali est libre jeudi 23/10/2026 à 14 h 00 » ; un jour entier : « Karim Benali est disponible samedi 25/10/2026 » |
| **Nouveau métier** | le prestataire ajoute un métier à son profil | « Karim Benali propose maintenant : Maçon » |
| **Retour après une absence** | fin d'une fermeture de **2 jours ou plus**, à **8 h** (heure de Paris) le jour de la reprise ; fin d'une pause du profil ([Reprendre]) | « Léa Dubois reprend son activité ce vendredi 31/10/2026 » |

## Décisions prises par Claude le 21/10/2026 (à confirmer par Raphael)
- **Une seule notification « Créneau libre » par prestataire en 6 heures.** Ex. Karim rouvre 4 samedis de suite : ses abonnés ne sont prévenus qu'une fois.
- Une annulation **par le prestataire** (« malade ») ne prévient pas : l'horaire n'est pas vraiment libre.
- Les horaires d'un seul jour (clic droit dans « Mon agenda ») ne préviennent pas.
- Ne comptent pas comme une absence : une fermeture de moins de 2 jours, les horaires d'un seul jour, les jours de travaux d'un devis. Deux métiers fermés pour les mêmes congés : une seule notification. Une autre fermeture qui commence à la reprise : l'absence continue, on attend sa fin.
- Serveur arrêté : les retours des 2 derniers jours sont rattrapés au redémarrage, jamais envoyés deux fois.
- Les textes n'utilisent ni « il » ni « elle » (« reprend son activité »).
