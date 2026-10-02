-- rafals - schema_v12.sql (lot 5.1, 02/10/2026)
-- Paiement par carte (Stripe Connect) : compte Stripe du prestataire ; un paiement par rendez-vous paye par carte.
-- Traduction exacte du MLD valide par Raphael le 02/10/2026 (.doc/mld/MLD-lot-5.1-paiements.html).
-- Regles : RM-PAIEMENTS.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v13.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v12.sql

BEGIN;

ALTER TABLE prestataire ADD COLUMN stripe_compte         text;
ALTER TABLE prestataire ADD COLUMN stripe_pret           boolean NOT NULL DEFAULT false;
ALTER TABLE prestataire ADD COLUMN mandat_facturation_le timestamptz;
ALTER TABLE prestataire ADD CONSTRAINT prestataire_stripe_compte_unique UNIQUE (stripe_compte);
-- Pret a etre paye par carte : seulement avec un compte Stripe
ALTER TABLE prestataire ADD CONSTRAINT prestataire_stripe_pret_avec_compte CHECK (NOT stripe_pret OR stripe_compte IS NOT NULL);
COMMENT ON COLUMN prestataire.stripe_compte IS 'Numero du compte Stripe du prestataire (acct_...), vide tant que la carte n''est pas activee.';
COMMENT ON COLUMN prestataire.stripe_pret IS 'Stripe a fini de verifier son identite : il peut etre paye par carte.';
COMMENT ON COLUMN prestataire.mandat_facturation_le IS 'Date de son accord pour que rafals fasse ses factures a sa place (RM-FACTURES).';

CREATE TABLE paiement (
  id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  rendez_vous_id        bigint      NOT NULL REFERENCES rendez_vous (id) ON DELETE RESTRICT,
  montant_centimes      integer     NOT NULL,
  commission_centimes   integer     NOT NULL,
  statut                text        NOT NULL DEFAULT 'a_payer',
  stripe_paiement       text,
  cree_le               timestamptz NOT NULL DEFAULT now(),
  paye_le               timestamptz,
  frais_stripe_centimes integer,
  verse_le              timestamptz,
  stripe_versement      text,
  rembourse_le          timestamptz,
  rembourse_centimes    integer,
  stripe_remboursement  text,
  CONSTRAINT paiement_un_par_rendez_vous UNIQUE (rendez_vous_id),
  CONSTRAINT paiement_stripe_paiement_unique UNIQUE (stripe_paiement),
  CONSTRAINT paiement_statut_connu CHECK (statut IN ('a_payer', 'paye', 'verse', 'rembourse', 'abandonne')),
  CONSTRAINT paiement_montant_positif CHECK (montant_centimes > 0),
  CONSTRAINT paiement_commission_valide CHECK (commission_centimes >= 0 AND commission_centimes <= montant_centimes),
  CONSTRAINT paiement_frais_valides CHECK (frais_stripe_centimes IS NULL OR frais_stripe_centimes >= 0),
  -- Paye, verse ou rembourse : forcement passe par Stripe, avec une date de paiement
  CONSTRAINT paiement_paye_date CHECK (statut IN ('a_payer', 'abandonne') OR (paye_le IS NOT NULL AND stripe_paiement IS NOT NULL)),
  CONSTRAINT paiement_verse_coherent CHECK ((statut = 'verse') = (verse_le IS NOT NULL)),
  -- Rembourse : une date et un montant, ensemble, jamais plus que ce qui a ete paye
  CONSTRAINT paiement_rembourse_coherent CHECK ((statut = 'rembourse') = (rembourse_le IS NOT NULL)
                                                AND (rembourse_le IS NULL) = (rembourse_centimes IS NULL)),
  CONSTRAINT paiement_rembourse_valide CHECK (rembourse_centimes IS NULL OR (rembourse_centimes >= 0 AND rembourse_centimes <= montant_centimes))
);
COMMENT ON TABLE paiement IS 'Paiement par carte d''un rendez-vous (Stripe). Jamais efface. Sommes en centimes.';
COMMENT ON COLUMN paiement.rendez_vous_id IS 'Rendez-vous paye ; passe au nouveau rendez-vous quand il est deplace.';
COMMENT ON COLUMN paiement.commission_centimes IS 'Les 5 % de rafals (RM-PAIEMENTS).';
COMMENT ON COLUMN paiement.verse_le IS 'L''argent, bloque sur le compte Stripe du prestataire, est parti vers sa banque (48 h apres la fin).';

COMMIT;
