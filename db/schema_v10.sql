-- rafals - schema_v10.sql (lot 4.5, 01/10/2026)
-- Absences sur un rendez-vous : signalement, contestation, decision de l'administrateur.
-- Traduction exacte du MLD valide par Raphael le 01/10/2026 (.doc/mld/MLD-lot-4.5-absences.html).
-- Regles : RM-RENDEZ-VOUS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v11.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v10.sql

BEGIN;

ALTER TABLE rendez_vous ADD COLUMN absent text;
ALTER TABLE rendez_vous ADD COLUMN absence_signalee_le timestamptz;
ALTER TABLE rendez_vous ADD COLUMN contestation text;
ALTER TABLE rendez_vous ADD COLUMN contestee_le timestamptz;
ALTER TABLE rendez_vous ADD COLUMN absence_decision text;
ALTER TABLE rendez_vous ADD COLUMN absence_decide_par_id bigint REFERENCES compte (id) ON DELETE RESTRICT;
ALTER TABLE rendez_vous ADD COLUMN absence_decide_le timestamptz;

ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_absent_connu CHECK (absent IS NULL OR absent IN ('client', 'prestataire'));
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_absence_datee CHECK ((absent IS NULL) = (absence_signalee_le IS NULL));
-- Une contestation : un texte et une date, seulement sur une absence signalee
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_contestation_coherente
  CHECK ((contestation IS NULL) = (contestee_le IS NULL) AND (contestee_le IS NULL OR absent IS NOT NULL));
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_decision_connue
  CHECK (absence_decision IS NULL OR absence_decision IN ('compte', 'ne_compte_pas'));
-- Une decision : seulement sur une absence contestee, avec son auteur et sa date
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_decision_coherente
  CHECK ((absence_decision IS NULL) = (absence_decide_le IS NULL) AND (absence_decision IS NULL) = (absence_decide_par_id IS NULL)
         AND (absence_decision IS NULL OR contestee_le IS NOT NULL));
CREATE INDEX rendez_vous_absences_idx ON rendez_vous (absent) WHERE absent IS NOT NULL;

COMMENT ON COLUMN rendez_vous.absent IS 'Qui n''est pas venu : client ou prestataire ; vide = personne.';
COMMENT ON COLUMN rendez_vous.contestation IS 'Explication de la personne marquee absente (« Je suis venu… »), dans les 7 jours.';
COMMENT ON COLUMN rendez_vous.absence_decision IS 'Decision de l''administrateur sur une contestation : compte ou ne_compte_pas.';

COMMIT;
