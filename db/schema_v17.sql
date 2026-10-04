-- rafals - schema_v17.sql (lot 6.3, 04/10/2026)
-- Signalements d'annonces et de prestataires ; choix « chaque mois / chaque trimestre » et rappels de declaration URSSAF.
-- Traduction exacte du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-lot-6.3-signalements-rappels.html).
-- Regles : RM-ADMINISTRATION.md, RM-DEMARCHES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v18.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v17.sql

BEGIN;

ALTER TABLE prestataire ADD COLUMN declaration_periodicite text;
ALTER TABLE prestataire ADD CONSTRAINT prestataire_declaration_periodicite_connue
  CHECK (declaration_periodicite IS NULL OR declaration_periodicite IN ('mois', 'trimestre'));
COMMENT ON COLUMN prestataire.declaration_periodicite IS 'Declaration URSSAF chaque mois ou chaque trimestre ; vide : il ne l''a pas dit, pas de rappel (RM-DEMARCHES).';

CREATE TABLE signalement (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  auteur_id      bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  annonce_id     bigint      REFERENCES annonce (id) ON DELETE RESTRICT,
  traite_par_id  bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  motif          text        NOT NULL,
  cree_le        timestamptz NOT NULL DEFAULT now(),
  statut         text        NOT NULL DEFAULT 'a_traiter',
  decision       text,
  traite_le      timestamptz,
  CONSTRAINT signalement_statut_connu CHECK (statut IN ('a_traiter', 'classe', 'suivi')),
  CONSTRAINT signalement_motif_longueur CHECK (length(motif) BETWEEN 10 AND 1000),
  -- Traite (classe ou suivi) : une date et son auteur, ensemble
  CONSTRAINT signalement_traite_coherent CHECK ((statut = 'a_traiter') = (traite_le IS NULL)
                                                AND (traite_le IS NULL) = (traite_par_id IS NULL))
);
CREATE INDEX signalement_prestataire_id_idx ON signalement (prestataire_id);
CREATE INDEX signalement_auteur_id_idx ON signalement (auteur_id);
COMMENT ON TABLE signalement IS 'Signalement d''une annonce ou d''un prestataire par un utilisateur (RM-ADMINISTRATION). Jamais efface ; l''auteur n''est jamais nomme au prestataire.';

CREATE TABLE rappel_declaration (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  periode_debut  date        NOT NULL,
  sorte          text        NOT NULL,
  envoye_le      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT rappel_declaration_sorte_connue CHECK (sorte IN ('sept_jours', 'veille')),
  -- Jamais deux fois le meme rappel
  CONSTRAINT rappel_declaration_unique UNIQUE (prestataire_id, periode_debut, sorte)
);
COMMENT ON TABLE rappel_declaration IS 'Rappels de declaration URSSAF deja envoyes (7 jours avant, la veille) : sert a ne pas les envoyer deux fois.';

COMMIT;
