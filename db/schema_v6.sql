-- rafals - schema_v6.sql (lot 2.6, 29/09/2026)
-- Adresse du client, fermeture de compte, comptes inactifs.
-- Traduction exacte du MLD valide par Raphael le 29/09/2026 (.doc/mld/MLD-lot-2.6-clients.html).
-- Regles : RM-CLIENTS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v7.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v6.sql

BEGIN;

ALTER TABLE compte ADD COLUMN ferme_le timestamptz;
ALTER TABLE compte ADD COLUMN inactivite_prevenue_le timestamptz;
-- Effacees a la fermeture du compte (la loi l'exige) ; toujours exigees a l'inscription par le serveur
ALTER TABLE compte ALTER COLUMN telephone DROP NOT NULL;
ALTER TABLE compte ALTER COLUMN date_naissance DROP NOT NULL;
COMMENT ON COLUMN compte.ferme_le IS 'Date de fermeture ; vide = compte ouvert. Un compte ferme ne garde rien de personnel.';
COMMENT ON COLUMN compte.inactivite_prevenue_le IS 'Mail « compte ferme dans 30 jours » (3 ans sans connexion) ; vide = pas prevenu.';

CREATE TABLE adresse (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id   bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  commune_id  bigint      NOT NULL REFERENCES commune (id) ON DELETE RESTRICT,
  ligne       text        NOT NULL,
  complement  text,
  code_postal text        NOT NULL,
  modifiee_le timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT adresse_une_par_compte UNIQUE (compte_id),
  CONSTRAINT adresse_code_postal_format CHECK (code_postal ~ '^[0-9]{5}$')
);
CREATE INDEX adresse_commune_id_idx ON adresse (commune_id);
COMMENT ON TABLE adresse IS 'Adresse du client, demandee seulement pour un service a domicile ; modifiable et effacable.';

COMMIT;
