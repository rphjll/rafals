-- rafals - schema_v32.sql (hors lot, 21/10/2026)
-- Notifications des abonnements : 3 cases dans les Parametres du compte (pour tous ses abonnements),
-- et un seul bouton « Rendre muet » par abonnement a la place des 3 cases par prestataire.
-- Traduction du MLD valide par Raphael le 21/10/2026 (« oui » ; .doc/mld/MLD-abonnement-defaut.html, 2e version).
-- Suppression accordee par Raphael le meme jour : les 3 cases notif_* de la table abonnement.
-- Ne jamais modifier ce fichier une fois execute : une correction = schema_v33.sql.
--
-- Avant (compte le 21/10/2026) : rafals_db 1 abonnement (zztest.karim@example.com -> raphael, 3 cases a oui),
-- rafals_test_db 10 lignes de test.
--
-- Execution (une seule fois par base, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v32.sql

BEGIN;

-- Les 3 cases de « Parametres », valables pour tous les abonnements du compte (oui au depart)
-- (ex. Julie : creneau = oui, nouveaute = non, retour = oui)
ALTER TABLE compte
  ADD COLUMN abo_notif_creneau   boolean NOT NULL DEFAULT true,   -- un creneau se libere
  ADD COLUMN abo_notif_nouveaute boolean NOT NULL DEFAULT true,   -- un nouveau metier
  ADD COLUMN abo_notif_retour    boolean NOT NULL DEFAULT true;   -- le retour apres une absence

-- Muet : plus aucune notification de ce prestataire, on reste abonne (ex. Julie -> Sophie, muet = oui)
ALTER TABLE abonnement ADD COLUMN muet boolean NOT NULL DEFAULT false;

-- Un abonnement dont les 3 cases etaient decochees devient muet (personne dans la vraie base le 21/10/2026)
UPDATE abonnement SET muet = true WHERE NOT notif_creneau AND NOT notif_nouveaute AND NOT notif_retour;

ALTER TABLE abonnement
  DROP COLUMN notif_creneau,
  DROP COLUMN notif_nouveaute,
  DROP COLUMN notif_retour;

COMMIT;
