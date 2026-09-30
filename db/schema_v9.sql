-- rafals - schema_v9.sql (lot 4.3, 30/09/2026)
-- Rendez-vous ; reglages de confirmation et d'annulation du prestataire.
-- Traduction exacte du MLD valide par Raphael le 30/09/2026 (.doc/mld/MLD-lot-4.3-rendez-vous.html).
-- Regles : RM-RENDEZ-VOUS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v10.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v9.sql

BEGIN;

-- Reglages (valeurs au depart : RM-RENDEZ-VOUS ; aussi dans backend/app/reglages.py)
ALTER TABLE prestataire ADD COLUMN confirmation_automatique boolean NOT NULL DEFAULT true;
ALTER TABLE prestataire ADD COLUMN annulation_delai_heures integer NOT NULL DEFAULT 24;
ALTER TABLE prestataire ADD CONSTRAINT prestataire_annulation_delai_connu CHECK (annulation_delai_heures IN (2, 12, 24, 48));
COMMENT ON COLUMN prestataire.confirmation_automatique IS 'Oui : un horaire libre est reserve aussitot ; non : « j''accepte chaque demande ».';
COMMENT ON COLUMN prestataire.annulation_delai_heures IS '« Annulation gratuite jusqu''a X avant » par le client : 2, 12, 24 ou 48 heures.';

CREATE TABLE rendez_vous (
  id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  client_id          bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  prestataire_id     bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  annonce_id         bigint      NOT NULL REFERENCES annonce (id) ON DELETE RESTRICT,
  commune_id         bigint      REFERENCES commune (id) ON DELETE RESTRICT,
  remplace_id        bigint      REFERENCES rendez_vous (id) ON DELETE RESTRICT,
  debut              timestamptz NOT NULL,
  fin                timestamptz NOT NULL,
  titre              text        NOT NULL,
  prix_centimes      integer,
  heures             integer,
  lieu               text        NOT NULL,
  adresse_ligne      text,
  adresse_complement text,
  code_postal        text,
  mode_paiement      text        NOT NULL,
  statut             text        NOT NULL,
  motif              text,
  cree_le            timestamptz NOT NULL DEFAULT now(),
  reponse_avant      timestamptz,
  statut_change_le   timestamptz NOT NULL DEFAULT now(),
  rappel_envoye_le   timestamptz,
  CONSTRAINT rendez_vous_fin_apres_debut CHECK (fin > debut),
  CONSTRAINT rendez_vous_prix_positif CHECK (prix_centimes IS NULL OR prix_centimes > 0),
  CONSTRAINT rendez_vous_heures_positives CHECK (heures IS NULL OR heures >= 1),
  CONSTRAINT rendez_vous_lieu_connu CHECK (lieu IN ('chez_client', 'chez_moi')),
  CONSTRAINT rendez_vous_paiement_connu CHECK (mode_paiement IN ('especes', 'carte')),
  CONSTRAINT rendez_vous_statut_connu CHECK (statut IN ('en_attente', 'confirme', 'refuse', 'expire', 'annule_client',
                                                        'annule_prestataire', 'deplace')),
  -- Une adresse recopiee (rue + ville) des qu'il y en a une
  CONSTRAINT rendez_vous_adresse_complete CHECK ((adresse_ligne IS NULL) = (commune_id IS NULL) AND (adresse_ligne IS NULL) = (code_postal IS NULL)),
  -- Une demande en attente a toujours une date limite de reponse
  CONSTRAINT rendez_vous_attente_limitee CHECK (statut <> 'en_attente' OR reponse_avant IS NOT NULL),
  CONSTRAINT rendez_vous_remplace_une_fois UNIQUE (remplace_id)
);
CREATE INDEX rendez_vous_client_id_idx ON rendez_vous (client_id);
CREATE INDEX rendez_vous_prestataire_debut_idx ON rendez_vous (prestataire_id, debut);
CREATE INDEX rendez_vous_annonce_id_idx ON rendez_vous (annonce_id);
COMMENT ON TABLE rendez_vous IS 'Horaire reserve par un client pour une annonce. Jamais efface. Titre, prix, duree et adresse recopies a la reservation.';
COMMENT ON COLUMN rendez_vous.remplace_id IS 'Rendez-vous deplace que celui-ci remplace (l''ancien passe « deplace »).';
COMMENT ON COLUMN rendez_vous.reponse_avant IS 'Fin des 24 h laissees au prestataire pour accepter une demande (ou l''heure du rendez-vous si plus tot).';

COMMIT;
