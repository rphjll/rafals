-- rafals - schema_v24.sql (07/10/2026)
-- Photos du travail d'un prestataire, montrees sur son profil et sur sa carte dans « Trouver un prestataire ».
-- Traduction du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-retrait-annonces.html), table PHOTO_PRESTATAIRE
-- seulement : demandee en avance sur le lot 9.1 par Raphael le 07/10/2026 (photos de travaux sur les cartes :
-- « Oui, tout de suite »). Les autres ajouts du lot 9.1 (lieu dans prestataire, demande_devis) viendront dans le
-- fichier suivant. Aucune table existante n'est touchee.
-- Regles : RM-PRESTATAIRES.md § « Sans annonces ». Ne jamais modifier ce fichier une fois execute : une correction = schema_v25.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v24.sql

BEGIN;

CREATE TABLE photo_prestataire (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint  NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  fichier_id     bigint  NOT NULL REFERENCES fichier (id) ON DELETE RESTRICT,
  ordre          integer NOT NULL,
  CONSTRAINT photo_prestataire_fichier_unique UNIQUE (fichier_id),
  CONSTRAINT photo_prestataire_ordre_unique UNIQUE (prestataire_id, ordre),
  CONSTRAINT photo_prestataire_ordre_valide CHECK (ordre BETWEEN 1 AND 10)
);
COMMENT ON TABLE photo_prestataire IS 'Photo du travail d''un prestataire (10 au plus), ex. une cuisine posee. A ne pas confondre avec prestataire.photo_id (sa photo de profil).';
COMMENT ON COLUMN photo_prestataire.ordre IS 'Ordre d''affichage, de 1 a 10 ; les 2 premieres sont montrees sur la carte de « Trouver un prestataire ».';

COMMIT;
