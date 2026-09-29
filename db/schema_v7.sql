-- rafals - schema_v7.sql (lot 3.1, 29/09/2026)
-- Annonces, photos d'annonce, local du prestataire, dates de fin de metier.
-- Traduction exacte du MLD valide par Raphael le 29/09/2026 (.doc/mld/MLD-lot-3.1-annonces.html).
-- Regles : RM-ANNONCES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v8.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v7.sql

BEGIN;

-- Dates de fin de metier (RM-ANNONCES : pas de bouton « supprimer ce metier »)
ALTER TABLE prestataire ADD COLUMN metier_principal_fin_le date;
ALTER TABLE prestataire ADD COLUMN metier_principal_suivant_id bigint REFERENCES metier (id) ON DELETE RESTRICT;
COMMENT ON COLUMN prestataire.metier_principal_fin_le IS 'Dernier jour du metier principal ; vide = pas de fin prevue.';
COMMENT ON COLUMN prestataire.metier_principal_suivant_id IS 'Metier secondaire qui devient principal apres la date de fin ; vide s''il n''y en a pas.';

ALTER TABLE metier_secondaire ADD COLUMN fin_le date;
COMMENT ON COLUMN metier_secondaire.fin_le IS 'Dernier jour de ce metier ; vide = pas de fin prevue.';

CREATE TABLE local (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  commune_id     bigint      NOT NULL REFERENCES commune (id) ON DELETE RESTRICT,
  ligne          text        NOT NULL,
  complement     text,
  code_postal    text        NOT NULL,
  modifie_le     timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT local_un_par_prestataire UNIQUE (prestataire_id),
  CONSTRAINT local_code_postal_format CHECK (code_postal ~ '^[0-9]{5}$')
);
CREATE INDEX local_commune_id_idx ON local (commune_id);
COMMENT ON TABLE local IS 'Salon ou atelier ou le prestataire recoit (annonces « chez moi ») ; la rue n''est montree qu''apres reservation.';

CREATE TABLE annonce (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id   bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  metier_id        bigint      NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  titre            text        NOT NULL,
  description      text,
  forme_prix       text        NOT NULL,
  prix_centimes    integer,
  duree_minutes    integer,
  heures_min       integer,
  heures_max       integer,
  lieu             text        NOT NULL,
  paiement_carte   boolean     NOT NULL DEFAULT false,
  paiement_especes boolean     NOT NULL DEFAULT true,
  statut           text        NOT NULL DEFAULT 'en_ligne',
  statut_change_le timestamptz NOT NULL DEFAULT now(),
  cree_le          timestamptz NOT NULL DEFAULT now(),
  modifiee_le      timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT annonce_forme_prix_connue CHECK (forme_prix IN ('fixe', 'heure', 'devis')),
  CONSTRAINT annonce_lieu_connu CHECK (lieu IN ('chez_client', 'chez_moi', 'les_deux')),
  CONSTRAINT annonce_statut_connu CHECK (statut IN ('en_ligne', 'en_pause', 'retiree')),
  CONSTRAINT annonce_un_paiement_au_moins CHECK (paiement_carte OR paiement_especes),
  -- Un prix pour « fixe » et « heure », aucun pour « devis »
  CONSTRAINT annonce_prix_coherent CHECK ((forme_prix = 'devis') = (prix_centimes IS NULL)),
  CONSTRAINT annonce_prix_positif CHECK (prix_centimes IS NULL OR prix_centimes > 0),
  -- Une duree seulement pour « fixe » ; des heures min et max seulement pour « heure »
  CONSTRAINT annonce_duree_coherente CHECK ((forme_prix = 'fixe') = (duree_minutes IS NOT NULL)),
  CONSTRAINT annonce_duree_positive CHECK (duree_minutes IS NULL OR duree_minutes > 0),
  CONSTRAINT annonce_heures_coherentes CHECK ((forme_prix = 'heure') = (heures_min IS NOT NULL AND heures_max IS NOT NULL)),
  CONSTRAINT annonce_heures_ordonnees CHECK (heures_min IS NULL OR (heures_min >= 1 AND heures_max >= heures_min))
);
CREATE INDEX annonce_prestataire_id_idx ON annonce (prestataire_id);
CREATE INDEX annonce_metier_id_idx ON annonce (metier_id);
COMMENT ON TABLE annonce IS 'Service propose par un prestataire (ex. « Menage 2 h - 50 € »). Jamais effacee : pause ou retrait.';
COMMENT ON COLUMN annonce.prix_centimes IS 'Prix en centimes (5000 = 50,00 €) ; prix de l''heure si forme_prix = heure.';
COMMENT ON COLUMN annonce.paiement_carte IS 'Souhait du prestataire ; la carte n''est proposee que si son SIRET est verifie au moment de reserver.';

CREATE TABLE photo_annonce (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  annonce_id bigint  NOT NULL REFERENCES annonce (id) ON DELETE RESTRICT,
  fichier_id bigint  NOT NULL REFERENCES fichier (id) ON DELETE RESTRICT,
  ordre      integer NOT NULL,
  CONSTRAINT photo_annonce_fichier_unique UNIQUE (fichier_id),
  CONSTRAINT photo_annonce_ordre_unique UNIQUE (annonce_id, ordre),
  CONSTRAINT photo_annonce_ordre_valide CHECK (ordre >= 1)
);
COMMENT ON TABLE photo_annonce IS 'Photo d''une annonce (5 au plus), la n° 1 est montree en premier.';

COMMIT;
