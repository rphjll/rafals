-- rafals - schema_v8.sql (lot 3.3, 30/09/2026)
-- Agenda : semaine type, blocages (conges, absences), reglages d'agenda du prestataire.
-- Traduction exacte du MLD valide par Raphael le 29/09/2026 (.doc/mld/MLD-lot-3.3-agenda.html).
-- Regles : RM-AGENDA.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v9.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v8.sql

BEGIN;

-- Reglages d'agenda (valeurs au depart = RM-AGENDA, « Valeurs par defaut » ; aussi dans backend/app/reglages.py)
ALTER TABLE prestataire ADD COLUMN agenda_pas_minutes integer NOT NULL DEFAULT 15;
ALTER TABLE prestataire ADD COLUMN agenda_pause_minutes integer NOT NULL DEFAULT 0;
ALTER TABLE prestataire ADD COLUMN reservation_delai_min_minutes integer NOT NULL DEFAULT 120;
ALTER TABLE prestataire ADD COLUMN reservation_delai_max_mois integer NOT NULL DEFAULT 2;
ALTER TABLE prestataire ADD CONSTRAINT prestataire_agenda_pas_connu CHECK (agenda_pas_minutes IN (15, 30, 60));
ALTER TABLE prestataire ADD CONSTRAINT prestataire_agenda_pause_positive CHECK (agenda_pause_minutes >= 0);
ALTER TABLE prestataire ADD CONSTRAINT prestataire_delai_min_positif CHECK (reservation_delai_min_minutes >= 0);
ALTER TABLE prestataire ADD CONSTRAINT prestataire_delai_max_positif CHECK (reservation_delai_max_mois >= 1);
COMMENT ON COLUMN prestataire.agenda_pas_minutes IS 'Ecart entre deux heures de debut proposees : 15, 30 ou 60 minutes.';
COMMENT ON COLUMN prestataire.agenda_pause_minutes IS 'Pause apres chaque rendez-vous (ex. trajet), rien n''est reservable pendant.';
COMMENT ON COLUMN prestataire.reservation_delai_min_minutes IS '« Au plus tot X avant » : 120 = 2 h.';
COMMENT ON COLUMN prestataire.reservation_delai_max_mois IS '« Au plus tard Y a l''avance » : 2 = 2 mois.';

CREATE TABLE plage_horaire (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint  NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  jour_semaine   integer NOT NULL,
  debut          time    NOT NULL,
  fin            time    NOT NULL,
  CONSTRAINT plage_horaire_jour_valide CHECK (jour_semaine BETWEEN 1 AND 7),
  CONSTRAINT plage_horaire_fin_apres_debut CHECK (fin > debut)
);
CREATE INDEX plage_horaire_prestataire_id_idx ON plage_horaire (prestataire_id);
COMMENT ON TABLE plage_horaire IS 'Semaine type : plage de travail repetee chaque semaine (heure de Paris, ex. mardi 09:00-12:00).';
COMMENT ON COLUMN plage_horaire.jour_semaine IS '1 = lundi ... 7 = dimanche.';

CREATE TABLE blocage (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  debut          timestamptz NOT NULL,
  fin            timestamptz NOT NULL,
  motif          text,
  cree_le        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT blocage_fin_apres_debut CHECK (fin > debut)
);
CREATE INDEX blocage_prestataire_id_idx ON blocage (prestataire_id);
COMMENT ON TABLE blocage IS 'Conges ou absence : periode non reservable. Le motif n''est jamais montre aux clients.';

COMMIT;
