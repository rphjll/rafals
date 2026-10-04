-- rafals - schema_v19.sql (lot 7.1, 04/10/2026)
-- Correction de schema_v18.sql (tables encore vides) : il manquait le code postal de l'adresse et la ville du local,
-- et le numero de securite sociale des personnes nees en Corse contient une lettre (2A, 2B).
-- Regles : RM-CREATION-AUTO-ENTREPRISE.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v20.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v19.sql

BEGIN;

ALTER TABLE dossier_creation ADD COLUMN code_postal text;
ALTER TABLE dossier_creation ADD COLUMN local_commune_id bigint REFERENCES commune (id) ON DELETE RESTRICT;
ALTER TABLE dossier_creation ADD COLUMN local_code_postal text;
ALTER TABLE dossier_creation ADD CONSTRAINT dossier_creation_code_postal_format
  CHECK (code_postal IS NULL OR code_postal ~ '^[0-9]{5}$');
ALTER TABLE dossier_creation ADD CONSTRAINT dossier_creation_local_code_postal_format
  CHECK (local_code_postal IS NULL OR local_code_postal ~ '^[0-9]{5}$');
COMMENT ON COLUMN dossier_creation.code_postal IS 'Code postal du domicile (une ville peut en avoir plusieurs : Bordeaux 33000, 33100...).';
COMMENT ON COLUMN dossier_creation.local_commune_id IS 'Ville du local, seulement si lieu_travail = local.';

-- Ne en Corse : le departement s'ecrit 2A ou 2B dans le numero (ex. 1 98 03 2A 004 123 45)
ALTER TABLE dossier_creation DROP CONSTRAINT dossier_creation_numero_secu_format;
ALTER TABLE dossier_creation ADD CONSTRAINT dossier_creation_numero_secu_format
  CHECK (numero_secu IS NULL OR numero_secu ~ '^[0-9]{6}[0-9AB][0-9]{8}$');

COMMIT;
