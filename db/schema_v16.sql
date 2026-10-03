-- rafals - schema_v16.sql (refonte du calendrier, 03/10/2026)
-- Un calendrier par metier : metier_id dans plage_horaire et blocage ; ouvertures exceptionnelles ;
-- reglage « un rendez-vous dans un metier bloque les autres calendriers ».
-- Traduction exacte du MLD valide par Raphael le 03/10/2026 (.doc/mld/MLD-refonte-calendrier.html).
-- Regles : RM-AGENDA.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v17.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v16.sql

BEGIN;

-- Les deux tables sont vides (comptage du 03/10/2026 : 0 plage, 0 blocage) : la rubrique est obligatoire tout de suite.
ALTER TABLE plage_horaire ADD COLUMN metier_id bigint NOT NULL REFERENCES metier (id) ON DELETE RESTRICT;
CREATE INDEX plage_horaire_metier_id_idx ON plage_horaire (metier_id);
COMMENT ON COLUMN plage_horaire.metier_id IS 'Le calendrier concerne : un des metiers du prestataire (verifie par le serveur).';

ALTER TABLE blocage ADD COLUMN metier_id bigint NOT NULL REFERENCES metier (id) ON DELETE RESTRICT;
CREATE INDEX blocage_metier_id_idx ON blocage (metier_id);
COMMENT ON COLUMN blocage.metier_id IS 'Le calendrier concerne : un des metiers du prestataire (verifie par le serveur).';
COMMENT ON TABLE blocage IS 'Fermeture exceptionnelle (conges, absence) : periode non reservable dans le calendrier d''un metier. Le motif n''est jamais montre aux clients.';

CREATE TABLE ouverture (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  metier_id      bigint      NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  debut          timestamptz NOT NULL,
  fin            timestamptz NOT NULL,
  motif          text,
  cree_le        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT ouverture_fin_apres_debut CHECK (fin > debut)
);
CREATE INDEX ouverture_prestataire_id_idx ON ouverture (prestataire_id);
CREATE INDEX ouverture_metier_id_idx ON ouverture (metier_id);
COMMENT ON TABLE ouverture IS 'Ouverture exceptionnelle : periode reservable en plus de la semaine type, dans le calendrier d''un metier, sans arret du debut a la fin. Le motif n''est jamais montre aux clients.';

ALTER TABLE prestataire ADD COLUMN rendez_vous_bloque_autres_metiers boolean NOT NULL DEFAULT true;
COMMENT ON COLUMN prestataire.rendez_vous_bloque_autres_metiers IS 'Oui : un rendez-vous dans un metier rend la meme heure non reservable dans les autres calendriers.';

COMMIT;
