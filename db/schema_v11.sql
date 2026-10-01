-- rafals - schema_v11.sql (lot 4.7, 01/10/2026)
-- Avis des clients sur les prestataires ; liste des mots interdits.
-- Traduction exacte du MLD valide par Raphael le 01/10/2026 (.doc/mld/MLD-lot-4.7-avis.html).
-- Regles : RM-AVIS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v12.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v11.sql

BEGIN;

CREATE TABLE avis (
  id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  rendez_vous_id        bigint      NOT NULL REFERENCES rendez_vous (id) ON DELETE RESTRICT,
  client_id             bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  prestataire_id        bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  cache_par_id          bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  note                  integer     NOT NULL,
  texte                 text        NOT NULL,
  cree_le               timestamptz NOT NULL DEFAULT now(),
  modifie_le            timestamptz NOT NULL DEFAULT now(),
  retire_le             timestamptz,
  reponse               text,
  repondu_le            timestamptz,
  signale_le            timestamptz,
  signalement           text,
  signalement_traite_le timestamptz,
  cache_le              timestamptz,
  cache_motif           text,
  CONSTRAINT avis_un_par_rendez_vous UNIQUE (rendez_vous_id),
  CONSTRAINT avis_note_valide CHECK (note BETWEEN 1 AND 5),
  CONSTRAINT avis_reponse_datee CHECK ((reponse IS NULL) = (repondu_le IS NULL)),
  CONSTRAINT avis_signalement_date CHECK ((signalement IS NULL) = (signale_le IS NULL)),
  -- Cache par l'administrateur : une date, un motif et son auteur, ensemble
  CONSTRAINT avis_cache_coherent CHECK ((cache_le IS NULL) = (cache_motif IS NULL) AND (cache_le IS NULL) = (cache_par_id IS NULL))
);
CREATE INDEX avis_prestataire_id_idx ON avis (prestataire_id);
CREATE INDEX avis_client_id_idx ON avis (client_id);
COMMENT ON TABLE avis IS 'Avis d''un client apres un rendez-vous tenu (1 a 5 etoiles + texte). Jamais efface : retire ou cache.';
COMMENT ON COLUMN avis.signalement_traite_le IS 'L''administrateur a regarde le signalement et laisse l''avis.';

CREATE TABLE mot_interdit (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  ajoute_par_id bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  mot           text        NOT NULL,
  ajoute_le     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT mot_interdit_unique UNIQUE (mot),
  CONSTRAINT mot_interdit_minuscules CHECK (mot = lower(mot) AND length(mot) >= 2)
);
COMMENT ON TABLE mot_interdit IS 'Gros mots refuses dans les avis et les reponses (minuscules, sans accents). Liste modifiable par l''administrateur.';

COMMIT;
