-- rafals - schema_v20.sql (lot 7.3, 04/10/2026)
-- Declarer a l'URSSAF depuis rafals : l'accord du prestataire (mandat) et les declarations envoyees.
-- Traduction exacte du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-lot-7.3-declarer-urssaf.html).
-- Regles : RM-DEMARCHES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v21.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v20.sql

BEGIN;

CREATE TABLE mandat_urssaf (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  numero_secu    text,
  texte          text        NOT NULL,
  donne_le       timestamptz NOT NULL DEFAULT now(),
  retire_le      timestamptz,
  demonstration  boolean     NOT NULL DEFAULT false,
  -- 15 caracteres ; ne en Corse : 2A ou 2B (meme regle que dossier_creation)
  CONSTRAINT mandat_urssaf_numero_secu_format CHECK (numero_secu IS NULL OR numero_secu ~ '^[0-9]{6}[0-9AB][0-9]{8}$'),
  -- Le numero est la tant que l'accord est en cours, et efface des qu'il est retire
  CONSTRAINT mandat_urssaf_retire_coherent CHECK ((retire_le IS NULL) = (numero_secu IS NOT NULL))
);
CREATE INDEX mandat_urssaf_prestataire_id_idx ON mandat_urssaf (prestataire_id);
-- Un seul accord en cours par prestataire
CREATE UNIQUE INDEX mandat_urssaf_un_seul_en_cours ON mandat_urssaf (prestataire_id) WHERE retire_le IS NULL;
COMMENT ON TABLE mandat_urssaf IS 'Accord donne a rafals pour declarer a l''URSSAF a la place du prestataire (RM-DEMARCHES). Jamais efface ; le numero de securite sociale est vide au retrait.';

CREATE TABLE declaration_urssaf (
  id                        bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id            bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  mandat_id                 bigint      NOT NULL REFERENCES mandat_urssaf (id) ON DELETE RESTRICT,
  periodicite               text        NOT NULL,
  periode_debut             date        NOT NULL,
  nature                    text        NOT NULL,
  montant_rafals_centimes   integer     NOT NULL,
  montant_ailleurs_centimes integer     NOT NULL DEFAULT 0,
  cotisations_centimes      integer     NOT NULL,
  declaree_le               timestamptz NOT NULL DEFAULT now(),
  reference_urssaf          text,
  demonstration             boolean     NOT NULL DEFAULT false,
  CONSTRAINT declaration_urssaf_periodicite_connue CHECK (periodicite IN ('mois', 'trimestre')),
  CONSTRAINT declaration_urssaf_nature_connue CHECK (nature IN ('services', 'liberale')),
  CONSTRAINT declaration_urssaf_montants_positifs CHECK (montant_rafals_centimes >= 0 AND montant_ailleurs_centimes >= 0
                                                         AND cotisations_centimes >= 0),
  -- Le 1er jour d'un mois ; pour un trimestre : janvier, avril, juillet ou octobre
  CONSTRAINT declaration_urssaf_periode_debut_valide CHECK (
    EXTRACT(DAY FROM periode_debut) = 1
    AND (periodicite = 'mois' OR EXTRACT(MONTH FROM periode_debut) IN (1, 4, 7, 10))),
  -- Jamais deux declarations de la meme periode
  CONSTRAINT declaration_urssaf_unique UNIQUE (prestataire_id, periodicite, periode_debut)
);
CREATE INDEX declaration_urssaf_mandat_id_idx ON declaration_urssaf (mandat_id);
COMMENT ON TABLE declaration_urssaf IS 'Declaration de chiffre d''affaires envoyee a l''URSSAF depuis rafals (RM-DEMARCHES). Jamais modifiee ni effacee : la preuve de ce qui a ete envoye.';
COMMENT ON COLUMN declaration_urssaf.montant_rafals_centimes IS 'Encaisse sur rafals pour la periode, fige au moment de l''envoi.';

COMMIT;
