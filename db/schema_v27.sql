-- rafals - schema_v27.sql (lot 8.5, 12/10/2026)
-- Avis d'un prestataire sur un client, alertes des prestataires, signalement d'une demande.
-- Traduction du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-niveau-8-demandes.html), partie « lot 8.5 » :
-- AVIS_CLIENT, ALERTE_COUPEE, 5 rubriques dans PRESTATAIRE, 1 rubrique dans COMPTE, SIGNALEMENT.demande_id.
-- Regles : RM-AVIS.md (§ « Notation dans les deux sens »), RM-ALERTES.md.
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v28.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v27.sql

BEGIN;

-- Memes rubriques que la table avis (l'avis du client sur le prestataire), dans l'autre sens
CREATE TABLE avis_client (
  id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  rendez_vous_id        bigint      NOT NULL REFERENCES rendez_vous (id) ON DELETE RESTRICT,
  prestataire_id        bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  client_id             bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
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
  CONSTRAINT avis_client_un_par_rendez_vous UNIQUE (rendez_vous_id),
  CONSTRAINT avis_client_note_valide CHECK (note BETWEEN 1 AND 5),
  CONSTRAINT avis_client_reponse_datee CHECK ((reponse IS NULL) = (repondu_le IS NULL)),
  CONSTRAINT avis_client_signalement_date CHECK ((signalement IS NULL) = (signale_le IS NULL)),
  -- Cache par l'administrateur : une date, un motif et son auteur, ensemble
  CONSTRAINT avis_client_cache_coherent CHECK ((cache_le IS NULL) = (cache_motif IS NULL) AND (cache_le IS NULL) = (cache_par_id IS NULL))
);
CREATE INDEX avis_client_client_id_idx ON avis_client (client_id);
CREATE INDEX avis_client_prestataire_id_idx ON avis_client (prestataire_id);
COMMENT ON TABLE avis_client IS 'Avis d''un prestataire sur un client apres un rendez-vous tenu (1 a 5 etoiles + texte). Jamais efface : retire ou cache. N''entre jamais dans le classement de la recherche.';

ALTER TABLE compte ADD COLUMN avis_recus_vus_le timestamptz;
COMMENT ON COLUMN compte.avis_recus_vus_le IS 'Derniere fois qu''il a ouvert « Mes avis recus » : sert au compteur rouge.';

-- « Ne pas me prevenir » pour un metier. Pas de ligne = prevenu (le reglage de depart).
CREATE TABLE alerte_coupee (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  metier_id      bigint      NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  cree_le        timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT alerte_coupee_unique UNIQUE (prestataire_id, metier_id)
);
COMMENT ON TABLE alerte_coupee IS 'Le prestataire ne veut pas etre prevenu des demandes de ce metier (RM-ALERTES).';

ALTER TABLE prestataire ADD COLUMN alerte_mail text NOT NULL DEFAULT 'chaque_demande';
ALTER TABLE prestataire ADD CONSTRAINT prestataire_alerte_mail_connue CHECK (alerte_mail IN ('chaque_demande', 'resume', 'aucun'));
ALTER TABLE prestataire ADD COLUMN demandes_vues_le timestamptz;
ALTER TABLE prestataire ADD COLUMN alertes_mail_jour date;
ALTER TABLE prestataire ADD COLUMN alertes_mail_nombre integer NOT NULL DEFAULT 0;
ALTER TABLE prestataire ADD COLUMN resume_envoye_le timestamptz;
COMMENT ON COLUMN prestataire.alerte_mail IS 'chaque_demande (au depart), resume (un seul mail a 18 h) ou aucun.';
COMMENT ON COLUMN prestataire.demandes_vues_le IS 'Derniere fois qu''il a ouvert « Demandes pres de chez moi » : sert au compteur rouge.';
COMMENT ON COLUMN prestataire.alertes_mail_nombre IS 'Mails de demandes envoyes le jour alertes_mail_jour (plafond de 20, ensuite tout va dans le resume).';
COMMENT ON COLUMN prestataire.resume_envoye_le IS 'Dernier resume de 18 h envoye.';

-- Signaler une demande (fausse, hors sujet, illegale) : il faut toujours au moins une cible
ALTER TABLE signalement ADD COLUMN demande_id bigint REFERENCES demande (id) ON DELETE RESTRICT;
ALTER TABLE signalement DROP CONSTRAINT signalement_cible_connue;
ALTER TABLE signalement ADD CONSTRAINT signalement_cible_connue
  CHECK (prestataire_id IS NOT NULL OR conversation_id IS NOT NULL OR demande_id IS NOT NULL);
CREATE INDEX signalement_demande_id_idx ON signalement (demande_id);
COMMENT ON COLUMN signalement.demande_id IS 'Demande signalee par un prestataire : l''administrateur la laisse ou la cache (RM-DEMANDES).';

COMMIT;
