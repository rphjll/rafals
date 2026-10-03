-- rafals - schema_v15.sql (lot 5.5, 03/10/2026)
-- Factures : ventes du prestataire, avoirs, commission mensuelle de rafals ; lignes ; [Paye] des rendez-vous en especes.
-- Traduction exacte du MLD valide par Raphael le 03/10/2026 (.doc/mld/MLD-lot-5.5-factures.html).
-- Regles : RM-FACTURES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v16.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v15.sql

BEGIN;

ALTER TABLE rendez_vous ADD COLUMN paye_direct_le    timestamptz;
ALTER TABLE rendez_vous ADD COLUMN paye_direct_moyen text;
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_paye_direct_coherent CHECK ((paye_direct_le IS NULL) = (paye_direct_moyen IS NULL));
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_paye_direct_moyen_connu
  CHECK (paye_direct_moyen IS NULL OR paye_direct_moyen IN ('especes', 'cheque', 'virement'));
COMMENT ON COLUMN rendez_vous.paye_direct_le IS 'Le prestataire a clique [Paye] : argent recu hors de rafals (RM-FACTURES).';

CREATE TABLE facture (
  id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id  bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  client_id       bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  rendez_vous_id  bigint      REFERENCES rendez_vous (id) ON DELETE RESTRICT,
  devis_id        bigint      REFERENCES devis (id) ON DELETE RESTRICT,
  paiement_id     bigint      REFERENCES paiement (id) ON DELETE RESTRICT,
  avoir_de_id     bigint      REFERENCES facture (id) ON DELETE RESTRICT,
  sorte           text        NOT NULL,
  annee           integer     NOT NULL,
  numero          integer     NOT NULL,
  emise_le        timestamptz NOT NULL DEFAULT now(),
  objet           text        NOT NULL,
  moyen_paiement  text,
  vendeur_nom     text        NOT NULL,
  vendeur_siret   text        NOT NULL,
  vendeur_adresse text        NOT NULL,
  acheteur_nom    text        NOT NULL,
  acheteur_adresse text,
  mention_tva     text,
  CONSTRAINT facture_sorte_connue CHECK (sorte IN ('vente', 'avoir', 'commission')),
  CONSTRAINT facture_numero_valide CHECK (numero >= 1 AND annee >= 2026),
  CONSTRAINT facture_moyen_connu CHECK (moyen_paiement IS NULL OR moyen_paiement IN ('carte', 'especes', 'cheque', 'virement')),
  -- Un avoir corrige une facture ; les autres n'en corrigent aucune
  CONSTRAINT facture_avoir_coherent CHECK ((sorte = 'avoir') = (avoir_de_id IS NOT NULL)),
  -- Vente ou avoir : un client ; commission (de rafals au prestataire) : pas de client
  CONSTRAINT facture_client_coherent CHECK ((sorte = 'commission') = (client_id IS NULL))
);
-- Numeros qui se suivent, sans doublon : F-... par prestataire et par annee (ventes et avoirs), R-... pour rafals
CREATE UNIQUE INDEX facture_numero_prestataire_unique ON facture (prestataire_id, annee, numero) WHERE sorte <> 'commission';
CREATE UNIQUE INDEX facture_numero_rafals_unique ON facture (annee, numero) WHERE sorte = 'commission';
CREATE INDEX facture_client_id_idx ON facture (client_id);
CREATE INDEX facture_paiement_id_idx ON facture (paiement_id);
COMMENT ON TABLE facture IS 'Factures (RM-FACTURES) : jamais modifiees ni effacees ; tout ce qui y est ecrit est fige a l''emission.';
COMMENT ON COLUMN facture.sorte IS 'vente (prestataire -> client), avoir (facture en moins), commission (rafals -> prestataire, une par mois).';

CREATE TABLE ligne_facture (
  id                     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  facture_id             bigint  NOT NULL REFERENCES facture (id) ON DELETE RESTRICT,
  ordre                  integer NOT NULL,
  libelle                text    NOT NULL,
  quantite_centiemes     integer NOT NULL,
  prix_unitaire_centimes integer NOT NULL,
  tva_pour_mille         integer,
  CONSTRAINT ligne_facture_ordre_unique UNIQUE (facture_id, ordre),
  CONSTRAINT ligne_facture_ordre_valide CHECK (ordre >= 1),
  CONSTRAINT ligne_facture_quantite_positive CHECK (quantite_centiemes > 0),
  CONSTRAINT ligne_facture_tva_connue CHECK (tva_pour_mille IS NULL OR tva_pour_mille IN (55, 100, 200))
);
COMMENT ON COLUMN ligne_facture.prix_unitaire_centimes IS 'Hors taxe si TVA ; peut etre negatif (arrhes deja payees, avoir).';

COMMIT;
