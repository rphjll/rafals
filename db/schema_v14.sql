-- rafals - schema_v14.sql (lot 5.3, 03/10/2026)
-- Correction de schema_v12.sql : un paiement « verse » a toujours une date de versement, mais un paiement rembourse
-- peut garder la sienne (arrhes deja versees au prestataire, puis rendues au client quand il annule le devis).
-- Decision de Raphael le 03/10/2026 (« Assouplir la regle »). Aucune donnee touchee.
-- Ne jamais modifier ce fichier une fois execute : une correction = schema_v15.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v14.sql

BEGIN;

ALTER TABLE paiement DROP CONSTRAINT paiement_verse_coherent;
-- Verse : forcement une date ; une date de versement : verse, ou rembourse apres coup
ALTER TABLE paiement ADD CONSTRAINT paiement_verse_coherent CHECK (
  (statut <> 'verse' OR verse_le IS NOT NULL) AND (verse_le IS NULL OR statut IN ('verse', 'rembourse')));
COMMENT ON COLUMN paiement.verse_le IS 'L''argent est parti vers la banque du prestataire ; garde si le paiement est rembourse ensuite.';

COMMIT;
