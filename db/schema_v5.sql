-- rafals - schema_v5.sql (lot 2.3, 28/09/2026)
-- Communes de France, profil prestataire, metiers secondaires.
-- Traduction exacte du MLD valide par Raphael le 28/09/2026 (.doc/mld/MLD-lot-2.3-prestataires.html).
-- Regles : RM-PRESTATAIRES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v6.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v5.sql

BEGIN;

CREATE TABLE commune (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  code_insee    text             NOT NULL,
  nom           text             NOT NULL,
  codes_postaux text[]           NOT NULL DEFAULT '{}',
  departement   text             NOT NULL,
  latitude      double precision NOT NULL,
  longitude     double precision NOT NULL,
  CONSTRAINT commune_code_insee_unique UNIQUE (code_insee),
  CONSTRAINT commune_latitude_valide CHECK (latitude BETWEEN -90 AND 90),
  CONSTRAINT commune_longitude_valide CHECK (longitude BETWEEN -180 AND 180)
);
COMMENT ON TABLE commune IS 'Liste officielle des communes de France (geo.api.gouv.fr), avec leur centre.';

CREATE TABLE prestataire (
  id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id           bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  metier_principal_id bigint      NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  commune_id          bigint      NOT NULL REFERENCES commune (id) ON DELETE RESTRICT,
  photo_id            bigint      REFERENCES fichier (id) ON DELETE RESTRICT,
  nom_affiche         text        NOT NULL,
  presentation        text,
  distance_km         integer     NOT NULL,
  siret               text,
  siret_statut        text        NOT NULL DEFAULT 'absent',
  siret_verifie_le    timestamptz,
  statut              text        NOT NULL DEFAULT 'actif',
  statut_change_le    timestamptz NOT NULL DEFAULT now(),
  cree_le             timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT prestataire_un_par_compte UNIQUE (compte_id),
  CONSTRAINT prestataire_photo_unique UNIQUE (photo_id),
  CONSTRAINT prestataire_distance_positive CHECK (distance_km > 0),
  CONSTRAINT prestataire_siret_format CHECK (siret IS NULL OR siret ~ '^[0-9]{14}$'),
  CONSTRAINT prestataire_siret_statut_connu CHECK (siret_statut IN ('absent', 'a_verifier', 'verifie', 'refuse')),
  -- Pas de SIRET <=> statut « absent »
  CONSTRAINT prestataire_siret_coherent CHECK ((siret IS NULL) = (siret_statut = 'absent')),
  CONSTRAINT prestataire_statut_connu CHECK (statut IN ('actif', 'en_pause', 'bloque', 'arrete'))
);
CREATE INDEX prestataire_metier_principal_id_idx ON prestataire (metier_principal_id);
CREATE INDEX prestataire_commune_id_idx ON prestataire (commune_id);
COMMENT ON TABLE prestataire IS 'Profil de quelqu''un qui propose ses services (un seul par compte).';
COMMENT ON COLUMN prestataire.statut IS 'actif, en_pause (par lui, reversible), bloque (par l''administrateur, reversible), arrete (definitif).';

CREATE TABLE metier_secondaire (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  metier_id      bigint NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  CONSTRAINT metier_secondaire_unique UNIQUE (prestataire_id, metier_id)
);
CREATE INDEX metier_secondaire_metier_id_idx ON metier_secondaire (metier_id);
COMMENT ON TABLE metier_secondaire IS 'Autre metier d''un prestataire (il apparait apres les specialistes dans les recherches).';

COMMIT;
