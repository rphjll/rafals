-- rafals - schema_v4.sql (lot 2.1, 28/09/2026)
-- Categories de metiers, metiers, propositions de metier.
-- Traduction exacte du MLD valide par Raphael le 28/09/2026 (.doc/mld/MLD-lot-2.1-metiers.html).
-- Regles : RM-METIERS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v5.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v4.sql

BEGIN;

-- Recherche sans tenir compte des accents (« electricien » trouve « Electricien »)
CREATE EXTENSION IF NOT EXISTS unaccent;

CREATE TABLE categorie_metier (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  code       text    NOT NULL,
  nom        text    NOT NULL,
  ordre      integer NOT NULL,
  est_active boolean NOT NULL DEFAULT true,
  CONSTRAINT categorie_metier_code_unique UNIQUE (code)
);
COMMENT ON TABLE categorie_metier IS 'Dossier qui regroupe des metiers voisins (ex. Maison & travaux).';

CREATE TABLE metier (
  id           bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  categorie_id bigint  NOT NULL REFERENCES categorie_metier (id) ON DELETE RESTRICT,
  code         text    NOT NULL,
  nom          text    NOT NULL,
  mots_cles    text[]  NOT NULL DEFAULT '{}',
  est_active   boolean NOT NULL DEFAULT true,
  CONSTRAINT metier_code_unique UNIQUE (code)
);
CREATE INDEX metier_categorie_id_idx ON metier (categorie_id);
COMMENT ON TABLE metier IS 'Activite professionnelle choisie dans la liste (ex. Plombier).';
COMMENT ON COLUMN metier.est_active IS 'Non = plus propose pour les nouvelles annonces ; les annonces existantes le gardent.';

CREATE TABLE proposition_metier (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  propose_par_id   bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  metier_retenu_id bigint      REFERENCES metier (id) ON DELETE RESTRICT,
  decide_par_id    bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  nom_propose      text        NOT NULL,
  statut           text        NOT NULL DEFAULT 'en_attente',
  propose_le       timestamptz NOT NULL DEFAULT now(),
  decide_le        timestamptz,
  CONSTRAINT proposition_statut_connu CHECK (statut IN ('en_attente', 'acceptee', 'remplacee', 'refusee')),
  -- En attente <=> pas encore de decision ; acceptee ou remplacee <=> un metier retenu
  CONSTRAINT proposition_decision_coherente CHECK ((statut = 'en_attente') = (decide_le IS NULL AND decide_par_id IS NULL)),
  CONSTRAINT proposition_metier_si_retenu CHECK ((statut IN ('acceptee', 'remplacee')) = (metier_retenu_id IS NOT NULL))
);
CREATE INDEX proposition_metier_propose_par_id_idx ON proposition_metier (propose_par_id);
COMMENT ON TABLE proposition_metier IS 'Metier propose par un prestataire qui ne trouve pas le sien, et la decision de l''administrateur.';

COMMIT;
