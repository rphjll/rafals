-- rafals - schema_v31.sql (hors lot, 21/10/2026)
-- S'abonner a un prestataire : la table ABONNEMENT.
-- Traduction du MLD valide par Raphael le 21/10/2026 (« oui » ; .doc/mld/MLD-abonnement.html).
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v32.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v31.sql

BEGIN;

-- Un compte qui suit un prestataire, avec les notifications qu'il a choisies pour lui
-- (ex. Julie suit Karim : creneau = oui, nouveaute = non, retour = oui)
CREATE TABLE abonnement (
  id              bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id       bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  prestataire_id  bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  notif_creneau   boolean     NOT NULL DEFAULT true,   -- un creneau se libere
  notif_nouveaute boolean     NOT NULL DEFAULT true,   -- un nouveau metier ou service
  notif_retour    boolean     NOT NULL DEFAULT true,   -- le retour apres une absence
  cree_le         timestamptz NOT NULL DEFAULT now(),
  -- Un meme compte ne suit qu'une fois le meme prestataire
  CONSTRAINT abonnement_un_par_couple UNIQUE (compte_id, prestataire_id)
);
-- L'index de la contrainte sert deja a chercher par compte ; celui-ci sert a compter les abonnes d'un prestataire
CREATE INDEX abonnement_prestataire_id_idx ON abonnement (prestataire_id);

COMMIT;
