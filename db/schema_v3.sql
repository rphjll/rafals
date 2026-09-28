-- rafals - schema_v3.sql (lot 1.3, 28/09/2026)
-- Role administrateur, fichiers, accord des parents, journal des actions.
-- Traduction exacte du MLD valide par Raphael le 28/09/2026
-- (.doc/mld/MLD-lot-1.3-accord-admin-journal.html). Regles : RM-COMPTES.md.
-- Ne jamais modifier ce fichier une fois execute : une correction = schema_v4.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v3.sql

BEGIN;

ALTER TABLE compte ADD COLUMN est_administrateur boolean NOT NULL DEFAULT false;
COMMENT ON COLUMN compte.est_administrateur IS 'Administrateur de rafals ; il reste toujours au moins un administrateur.';

CREATE TABLE fichier (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  depose_par_id bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  cle_stockage  text        NOT NULL,
  nom_origine   text        NOT NULL,
  type_mime     text        NOT NULL,
  taille_octets bigint      NOT NULL,
  depose_le     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT fichier_cle_unique UNIQUE (cle_stockage),
  CONSTRAINT fichier_taille_positive CHECK (taille_octets > 0)
);
CREATE INDEX fichier_depose_par_id_idx ON fichier (depose_par_id);
COMMENT ON TABLE fichier IS 'Fichier range dans le stockage (Garage en local, S3 en ligne).';
COMMENT ON COLUMN fichier.cle_stockage IS 'Nom de rangement dans le stockage, tire au hasard.';

CREATE TABLE accord_parental (
  id            bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id     bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  fichier_id    bigint      NOT NULL REFERENCES fichier (id) ON DELETE RESTRICT,
  decide_par_id bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  statut        text        NOT NULL DEFAULT 'en_attente',
  depose_le     timestamptz NOT NULL DEFAULT now(),
  decide_le     timestamptz,
  motif_refus   text,
  CONSTRAINT accord_fichier_unique UNIQUE (fichier_id),
  CONSTRAINT accord_statut_connu CHECK (statut IN ('en_attente', 'accepte', 'refuse')),
  -- En attente <=> pas encore de decision ; refuse <=> un motif
  CONSTRAINT accord_decision_coherente CHECK ((statut = 'en_attente') = (decide_le IS NULL AND decide_par_id IS NULL)),
  CONSTRAINT accord_motif_si_refus CHECK ((statut = 'refuse') = (motif_refus IS NOT NULL))
);
CREATE INDEX accord_parental_compte_id_idx ON accord_parental (compte_id);
COMMENT ON TABLE accord_parental IS 'Accord signe des parents d''un compte de 16 ou 17 ans, verifie par un administrateur.';

CREATE TABLE journal_action (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  auteur_id   bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  action      text        NOT NULL,
  table_cible text        NOT NULL,
  ligne_id    bigint,
  avant       jsonb,
  apres       jsonb,
  fait_le     timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX journal_action_cible_idx ON journal_action (table_cible, ligne_id);
COMMENT ON TABLE journal_action IS 'Qui a fait quoi, quand, avant/apres. On y ecrit, on n''y efface jamais.';
COMMENT ON COLUMN journal_action.auteur_id IS 'Vide = action faite par rafals tout seul.';

-- Le compte application peut ecrire et lire le journal, jamais le modifier ni l'effacer
REVOKE UPDATE, DELETE ON journal_action FROM rafals_app;

COMMIT;
