-- rafals - schema_v13.sql (lot 5.3, 03/10/2026)
-- Devis : demande du client (avec photos), devis en lignes, arrhes et solde payes par carte ; case « Je facture la TVA ».
-- Traduction exacte du MLD valide par Raphael le 03/10/2026 (.doc/mld/MLD-lot-5.3-devis.html).
-- Regles : RM-DEVIS.md, RM-PAIEMENTS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v14.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v13.sql

BEGIN;

ALTER TABLE prestataire ADD COLUMN facture_tva boolean NOT NULL DEFAULT false;
COMMENT ON COLUMN prestataire.facture_tva IS 'Case « Je facture la TVA » (RM-DEVIS) ; sinon mention « TVA non applicable, art. 293 B du CGI ».';

CREATE TABLE demande_devis (
  id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  client_id          bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  annonce_id         bigint      NOT NULL REFERENCES annonce (id) ON DELETE RESTRICT,
  prestataire_id     bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  commune_id         bigint      REFERENCES commune (id) ON DELETE RESTRICT,
  texte              text        NOT NULL,
  adresse_ligne      text,
  adresse_complement text,
  code_postal        text,
  statut             text        NOT NULL DEFAULT 'envoyee',
  motif              text,
  cree_le            timestamptz NOT NULL DEFAULT now(),
  statut_change_le   timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT demande_devis_statut_connu CHECK (statut IN ('envoyee', 'devis_recu', 'declinee', 'annulee')),
  CONSTRAINT demande_devis_texte_longueur CHECK (length(texte) BETWEEN 10 AND 2000),
  -- Lieu des travaux : une adresse complete, ou rien
  CONSTRAINT demande_devis_adresse_complete CHECK ((adresse_ligne IS NULL) = (commune_id IS NULL)
                                                   AND (adresse_ligne IS NULL) = (code_postal IS NULL))
);
CREATE INDEX demande_devis_client_id_idx ON demande_devis (client_id);
CREATE INDEX demande_devis_prestataire_id_idx ON demande_devis (prestataire_id);
COMMENT ON TABLE demande_devis IS 'Demande ecrite d''un client depuis une annonce « sur devis » (RM-DEVIS). Jamais effacee.';

CREATE TABLE photo_demande (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  demande_devis_id bigint  NOT NULL REFERENCES demande_devis (id) ON DELETE RESTRICT,
  fichier_id       bigint  NOT NULL REFERENCES fichier (id) ON DELETE RESTRICT,
  ordre            integer NOT NULL,
  CONSTRAINT photo_demande_fichier_unique UNIQUE (fichier_id),
  CONSTRAINT photo_demande_ordre_unique UNIQUE (demande_devis_id, ordre),
  CONSTRAINT photo_demande_ordre_valide CHECK (ordre >= 1)
);

CREATE TABLE devis (
  id                  bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  demande_devis_id    bigint      NOT NULL REFERENCES demande_devis (id) ON DELETE RESTRICT,
  blocage_id          bigint      REFERENCES blocage (id) ON DELETE RESTRICT,
  annee               integer     NOT NULL,
  numero              integer     NOT NULL,
  facture_tva         boolean     NOT NULL,
  arrhes_pourcent     integer     NOT NULL,
  travaux_debut       date        NOT NULL,
  travaux_fin         date        NOT NULL,
  valable_jusqu_au    date        NOT NULL,
  statut              text        NOT NULL DEFAULT 'envoye',
  mode_paiement       text,
  envoye_le           timestamptz NOT NULL DEFAULT now(),
  accepte_le          timestamptz,
  termine_le          timestamptz,
  paye_le             timestamptz,
  statut_change_le    timestamptz NOT NULL DEFAULT now(),
  message             text,
  probleme            text,
  probleme_le         timestamptz,
  probleme_traite_le  timestamptz,
  moyen_direct        text,
  CONSTRAINT devis_un_par_demande UNIQUE (demande_devis_id),
  CONSTRAINT devis_blocage_unique UNIQUE (blocage_id),
  CONSTRAINT devis_statut_connu CHECK (statut IN ('envoye', 'autre_date', 'accepte', 'termine', 'paye', 'refuse', 'expire',
                                                  'annule_client', 'annule_prestataire')),
  CONSTRAINT devis_mode_connu CHECK (mode_paiement IS NULL OR mode_paiement IN ('carte', 'direct')),
  CONSTRAINT devis_arrhes_valides CHECK (arrhes_pourcent BETWEEN 0 AND 100),
  CONSTRAINT devis_numero_valide CHECK (numero >= 1 AND annee >= 2026),
  CONSTRAINT devis_travaux_ordonnes CHECK (travaux_fin >= travaux_debut),
  -- Accepte (ou plus loin) : une date d'acceptation ; mode de paiement choisi en acceptant, et seulement alors
  CONSTRAINT devis_accepte_coherent CHECK ((accepte_le IS NULL) = (mode_paiement IS NULL)
                                           AND (statut NOT IN ('accepte', 'termine', 'paye') OR accepte_le IS NOT NULL)),
  CONSTRAINT devis_probleme_date CHECK ((probleme IS NULL) = (probleme_le IS NULL)),
  CONSTRAINT devis_moyen_direct_connu CHECK (moyen_direct IS NULL OR moyen_direct IN ('especes', 'cheque', 'virement'))
);
-- Numeros qui se suivent, sans doublon, par prestataire et par annee : le prestataire est retrouve par la demande,
-- l'unicite est donc garantie par le serveur (verrou sur le prestataire pendant la numerotation)
CREATE INDEX devis_annee_numero_idx ON devis (annee, numero);
COMMENT ON TABLE devis IS 'Devis d''un prestataire en reponse a une demande (RM-DEVIS). Jamais efface ; lignes figees apres l''envoi.';
COMMENT ON COLUMN devis.blocage_id IS 'Jours des travaux bloques dans l''agenda, a l''acceptation (enleve si le devis est annule).';
COMMENT ON COLUMN devis.message IS 'Autre date demandee par le client, ou motif d''un refus ou d''une annulation.';

CREATE TABLE ligne_devis (
  id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  devis_id              bigint  NOT NULL REFERENCES devis (id) ON DELETE RESTRICT,
  ordre                 integer NOT NULL,
  libelle               text    NOT NULL,
  quantite_centiemes    integer NOT NULL,
  prix_unitaire_centimes integer NOT NULL,
  tva_pour_mille        integer,
  CONSTRAINT ligne_devis_ordre_unique UNIQUE (devis_id, ordre),
  CONSTRAINT ligne_devis_ordre_valide CHECK (ordre >= 1),
  CONSTRAINT ligne_devis_libelle_longueur CHECK (length(libelle) BETWEEN 2 AND 200),
  CONSTRAINT ligne_devis_quantite_positive CHECK (quantite_centiemes > 0),
  CONSTRAINT ligne_devis_prix_valide CHECK (prix_unitaire_centimes >= 0),
  CONSTRAINT ligne_devis_tva_connue CHECK (tva_pour_mille IS NULL OR tva_pour_mille IN (55, 100, 200))
);
COMMENT ON COLUMN ligne_devis.quantite_centiemes IS '4000 = 40 ; 250 = 2,5 (m², heures...).';
COMMENT ON COLUMN ligne_devis.tva_pour_mille IS '55, 100 ou 200 (5,5 %, 10 %, 20 %) ; vide si le prestataire ne facture pas la TVA.';

-- Paiement : sur un rendez-vous OU sur un devis (arrhes, solde)
ALTER TABLE paiement ALTER COLUMN rendez_vous_id DROP NOT NULL;
ALTER TABLE paiement ADD COLUMN devis_id bigint REFERENCES devis (id) ON DELETE RESTRICT;
ALTER TABLE paiement ADD COLUMN sorte text NOT NULL DEFAULT 'rendez_vous';
ALTER TABLE paiement ADD CONSTRAINT paiement_sorte_connue CHECK (sorte IN ('rendez_vous', 'arrhes', 'solde'));
ALTER TABLE paiement ADD CONSTRAINT paiement_rendez_vous_ou_devis CHECK (
  (sorte = 'rendez_vous' AND rendez_vous_id IS NOT NULL AND devis_id IS NULL)
  OR (sorte IN ('arrhes', 'solde') AND devis_id IS NOT NULL AND rendez_vous_id IS NULL));
ALTER TABLE paiement ADD CONSTRAINT paiement_un_par_sorte_de_devis UNIQUE (devis_id, sorte);
CREATE INDEX paiement_devis_id_idx ON paiement (devis_id);
COMMENT ON COLUMN paiement.sorte IS 'rendez_vous ; arrhes ou solde d''un devis (RM-DEVIS).';

COMMIT;
