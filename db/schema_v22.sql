-- rafals - schema_v22.sql (lot 8.3, premiere partie, 06/10/2026)
-- Demandes publiees par les clients, et leurs photos.
-- Traduction du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-niveau-8-demandes.html), table DEMANDE,
-- plus l'adresse et sa position, demandees par Raphael le 05/10/2026 (« faut que on pussie metre l'adresse et que
-- y'ai une carte »). Les reponses, propositions et negociations viennent dans le fichier suivant.
-- La table des photos s'appelle photo_demande_publiee : photo_demande existe deja (photos d'une demande de devis).
-- Regles : RM-DEMANDES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v23.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v22.sql

BEGIN;

CREATE TABLE demande (
  id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  client_id          bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  metier_id          bigint      NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  commune_id         bigint      NOT NULL REFERENCES commune (id) ON DELETE RESTRICT,
  cachee_par_id      bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  titre              text        NOT NULL,
  description        text        NOT NULL,
  quand              text        NOT NULL,
  jour               date,
  lieu               text        NOT NULL DEFAULT 'chez_moi',
  budget_centimes    integer,
  adresse_ligne      text,
  adresse_complement text,
  code_postal        text,
  latitude           double precision,
  longitude          double precision,
  statut             text        NOT NULL DEFAULT 'ouverte',
  statut_change_le   timestamptz NOT NULL DEFAULT now(),
  cree_le            timestamptz NOT NULL DEFAULT now(),
  expire_le          timestamptz NOT NULL,
  rappel_envoye_le   timestamptz,
  cachee_le          timestamptz,
  cachee_motif       text,
  CONSTRAINT demande_titre_longueur CHECK (length(titre) BETWEEN 5 AND 80),
  CONSTRAINT demande_description_longueur CHECK (length(description) BETWEEN 20 AND 1000),
  CONSTRAINT demande_quand_connu CHECK (quand IN ('des_que_possible', 'sept_jours', 'jour_precis', 'pas_presse')),
  -- Une date seulement pour « un jour precis »
  CONSTRAINT demande_jour_coherent CHECK ((quand = 'jour_precis') = (jour IS NOT NULL)),
  CONSTRAINT demande_lieu_connu CHECK (lieu IN ('chez_moi', 'chez_prestataire')),
  CONSTRAINT demande_budget_positif CHECK (budget_centimes IS NULL OR budget_centimes > 0),
  CONSTRAINT demande_statut_connu CHECK (statut IN ('ouverte', 'pourvue', 'fermee', 'expiree')),
  CONSTRAINT demande_code_postal_format CHECK (code_postal IS NULL OR code_postal ~ '^[0-9]{5}$'),
  -- « Chez moi » : la rue est obligatoire (elle n'est montree qu'au prestataire choisi)
  CONSTRAINT demande_rue_si_chez_moi CHECK (lieu <> 'chez_moi' OR adresse_ligne IS NOT NULL),
  -- La position du repere sur le plan : les deux nombres ensemble, ou aucun
  CONSTRAINT demande_position_complete CHECK ((latitude IS NULL) = (longitude IS NULL)),
  CONSTRAINT demande_position_valide CHECK (latitude IS NULL OR (latitude BETWEEN -90 AND 90 AND longitude BETWEEN -180 AND 180)),
  -- Cachee par l'administrateur : une date et son auteur, ensemble
  CONSTRAINT demande_cachee_coherente CHECK ((cachee_le IS NULL) = (cachee_par_id IS NULL))
);
CREATE INDEX demande_client_id_idx ON demande (client_id);
CREATE INDEX demande_metier_id_idx ON demande (metier_id);
CREATE INDEX demande_commune_id_idx ON demande (commune_id);
CREATE INDEX demande_statut_cree_le_idx ON demande (statut, cree_le DESC);
COMMENT ON TABLE demande IS 'Besoin publie par un client (ex. « Tondre ma pelouse samedi a Pessac, 40 € »). Jamais effacee (RM-DEMANDES).';
COMMENT ON COLUMN demande.quand IS 'des_que_possible, sept_jours, jour_precis (voir jour) ou pas_presse.';
COMMENT ON COLUMN demande.adresse_ligne IS 'La rue : montree seulement au prestataire choisi ; les autres voient la ville (commune_id).';
COMMENT ON COLUMN demande.latitude IS 'Position de l''adresse, pour le repere du plan (vide si le client n''a donne que sa ville).';
COMMENT ON COLUMN demande.expire_le IS '30 jours apres la publication, ou la fin du jour demande s''il arrive avant.';
COMMENT ON COLUMN demande.rappel_envoye_le IS 'Le mail « votre demande se ferme dans 3 jours » est parti.';

CREATE TABLE photo_demande_publiee (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  demande_id bigint  NOT NULL REFERENCES demande (id) ON DELETE RESTRICT,
  fichier_id bigint  NOT NULL REFERENCES fichier (id) ON DELETE RESTRICT,
  ordre      integer NOT NULL,
  CONSTRAINT photo_demande_publiee_fichier_unique UNIQUE (fichier_id),
  CONSTRAINT photo_demande_publiee_ordre_unique UNIQUE (demande_id, ordre),
  CONSTRAINT photo_demande_publiee_ordre_valide CHECK (ordre BETWEEN 1 AND 5)
);
COMMENT ON TABLE photo_demande_publiee IS 'Photo jointe a une demande publiee (5 au plus). A ne pas confondre avec photo_demande (demande de devis).';

COMMIT;
