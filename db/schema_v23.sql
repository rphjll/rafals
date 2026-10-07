-- rafals - schema_v23.sql (lot 8.3, seconde partie, 07/10/2026)
-- Reponses a une demande, propositions, negociations du prix ; un rendez-vous peut venir d'une proposition
-- et porte lui-meme son metier.
-- Traduction des MLD valides par Raphael : .doc/mld/MLD-niveau-8-demandes.html (04/10/2026 : REPONSE_DEMANDE,
-- PROPOSITION, NEGOCIATION, RENDEZ_VOUS.proposition_id, annonce_id facultative) et
-- .doc/mld/MLD-retrait-annonces.html (04/10/2026 : RENDEZ_VOUS.metier_id).
-- Regles : RM-DEMANDES.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v24.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v23.sql

BEGIN;

CREATE TABLE reponse_demande (
  id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  demande_id      bigint      NOT NULL REFERENCES demande (id) ON DELETE RESTRICT,
  prestataire_id  bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  conversation_id bigint      NOT NULL REFERENCES conversation (id) ON DELETE RESTRICT,
  cree_le         timestamptz NOT NULL DEFAULT now(),
  -- Un prestataire repond une seule fois a une demande
  CONSTRAINT reponse_demande_une_par_prestataire UNIQUE (demande_id, prestataire_id)
);
CREATE INDEX reponse_demande_prestataire_id_idx ON reponse_demande (prestataire_id);
CREATE INDEX reponse_demande_conversation_id_idx ON reponse_demande (conversation_id);
COMMENT ON TABLE reponse_demande IS '« Karim a repondu a cette demande » : une ligne par prestataire et par demande (10 au plus par demande).';

CREATE TABLE proposition (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  conversation_id  bigint      NOT NULL REFERENCES conversation (id) ON DELETE RESTRICT,
  demande_id       bigint      REFERENCES demande (id) ON DELETE RESTRICT,
  metier_id        bigint      NOT NULL REFERENCES metier (id) ON DELETE RESTRICT,
  remplace_id      bigint      REFERENCES proposition (id) ON DELETE RESTRICT,
  prix_centimes    integer     NOT NULL,
  debut            timestamptz NOT NULL,
  fin              timestamptz NOT NULL,
  lieu             text        NOT NULL,
  paiement_carte   boolean     NOT NULL DEFAULT false,
  paiement_especes boolean     NOT NULL DEFAULT true,
  statut           text        NOT NULL DEFAULT 'en_attente',
  statut_change_le timestamptz NOT NULL DEFAULT now(),
  cree_le          timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT proposition_prix_positif CHECK (prix_centimes > 0),
  CONSTRAINT proposition_fin_apres_debut CHECK (fin > debut),
  CONSTRAINT proposition_lieu_connu CHECK (lieu IN ('chez_client', 'chez_moi')),
  CONSTRAINT proposition_un_paiement_au_moins CHECK (paiement_carte OR paiement_especes),
  CONSTRAINT proposition_statut_connu CHECK (statut IN ('en_attente', 'acceptee', 'refusee', 'retiree', 'remplacee',
                                                        'non_retenue', 'expiree')),
  CONSTRAINT proposition_remplace_une_fois UNIQUE (remplace_id)
);
CREATE INDEX proposition_conversation_id_idx ON proposition (conversation_id);
CREATE INDEX proposition_demande_id_idx ON proposition (demande_id);
COMMENT ON TABLE proposition IS 'Prix, jour, heure et lieu proposes par un prestataire a un client, dans leur conversation (RM-DEMANDES). Jamais effacee.';
COMMENT ON COLUMN proposition.demande_id IS 'La demande publiee a laquelle elle repond ; vide : le client a ecrit en premier, sans demande.';
COMMENT ON COLUMN proposition.metier_id IS 'Dit dans quel calendrier tombera le rendez-vous (celui de la demande, ou choisi par le prestataire).';
COMMENT ON COLUMN proposition.remplace_id IS 'La proposition qu''elle remplace (nouvelle proposition, ou prix negocie accepte).';

CREATE TABLE negociation (
  id             bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  proposition_id bigint      NOT NULL REFERENCES proposition (id) ON DELETE RESTRICT,
  prix_centimes  integer     NOT NULL,
  statut         text        NOT NULL DEFAULT 'en_attente',
  cree_le        timestamptz NOT NULL DEFAULT now(),
  repondu_le     timestamptz,
  CONSTRAINT negociation_prix_positif CHECK (prix_centimes > 0),
  CONSTRAINT negociation_statut_connu CHECK (statut IN ('en_attente', 'acceptee', 'refusee')),
  -- Repondue : une date ; en attente : aucune
  CONSTRAINT negociation_reponse_coherente CHECK ((statut = 'en_attente') = (repondu_le IS NULL))
);
-- Une seule negociation a la fois par proposition
CREATE UNIQUE INDEX negociation_une_en_attente_idx ON negociation (proposition_id) WHERE statut = 'en_attente';
CREATE INDEX negociation_proposition_id_idx ON negociation (proposition_id);
COMMENT ON TABLE negociation IS '[Negocier le prix] : le prix plus bas propose par le client, accepte ou refuse par le prestataire.';

-- Un rendez-vous vient d'une annonce OU d'une proposition, et porte son metier (avant : lu dans l'annonce)
ALTER TABLE rendez_vous ADD COLUMN proposition_id bigint REFERENCES proposition (id) ON DELETE RESTRICT;
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_proposition_unique UNIQUE (proposition_id);
ALTER TABLE rendez_vous ADD COLUMN metier_id bigint REFERENCES metier (id) ON DELETE RESTRICT;
UPDATE rendez_vous r SET metier_id = a.metier_id FROM annonce a WHERE a.id = r.annonce_id;
ALTER TABLE rendez_vous ALTER COLUMN metier_id SET NOT NULL;
ALTER TABLE rendez_vous ALTER COLUMN annonce_id DROP NOT NULL;
ALTER TABLE rendez_vous ADD CONSTRAINT rendez_vous_origine_connue CHECK (annonce_id IS NOT NULL OR proposition_id IS NOT NULL);
CREATE INDEX rendez_vous_metier_id_idx ON rendez_vous (metier_id);
COMMENT ON COLUMN rendez_vous.proposition_id IS 'La proposition acceptee dont vient ce rendez-vous (vide s''il vient d''une annonce).';
COMMENT ON COLUMN rendez_vous.metier_id IS 'Le calendrier ou tombe le rendez-vous : le metier de l''annonce ou de la proposition, recopie.';

COMMIT;
