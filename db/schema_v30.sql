-- rafals - schema_v30.sql (hors lot, 18/10/2026)
-- L'argent encaisse ailleurs, ajoute a la barre de TVA de « Mon activite » : la table ENCAISSE_AILLEURS.
-- Traduction du MLD valide par Raphael le 18/10/2026 (« oui » ; .doc/mld/MLD-encaisse-ailleurs.html).
-- Regles : RM-MON-ACTIVITE.md (§ « La barre de la TVA »).
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v31.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v30.sql

BEGIN;

-- Un montant encaisse en dehors de rafals, declare par le prestataire (ex. 2 000,00 EUR le 03/02/2026 = 200000)
CREATE TABLE encaisse_ailleurs (
  id               bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  prestataire_id   bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  montant_centimes integer     NOT NULL,
  encaisse_le      date        NOT NULL,
  cree_le          timestamptz NOT NULL DEFAULT now(),
  -- Toujours plus grand que 0 (une erreur se supprime, elle ne se compense pas par un montant negatif)
  CONSTRAINT encaisse_ailleurs_montant_positif CHECK (montant_centimes > 0)
);
CREATE INDEX encaisse_ailleurs_prestataire_id_idx ON encaisse_ailleurs (prestataire_id);

COMMIT;
