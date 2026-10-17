-- rafals - schema_v29.sql (lot 9.4, 17/10/2026)
-- Les tables des annonces disparaissent.
-- Traduction du MLD valide par Raphael le 17/10/2026 (« A » ; .doc/mld/MLD-lot-9.4-suppression-annonces.html),
-- qui reprend la partie « supprimees » du MLD du 04/10/2026 (.doc/mld/MLD-retrait-annonces.html).
-- Lignes effacees avec l'accord de Raphael du 17/10/2026 (« A tu peux tout supr ») : annonces 15 et 16, rendez-vous
-- 6, 7, 8 et 9 (tous de l'annonce 15), leurs 2 factures (2 et 3, avec leurs lignes) et leur avis. Rien d'autre.
-- Copie de securite faite avant : db-sync/securite/avant_lot_9.4_20261017_143233.sql
-- Ne jamais modifier ce fichier une fois execute : une correction = schema_v30.sql.
-- (Premier essai le 17/10/2026 arrete par la base, tout annule : le lien des demandes de devis partait trop tard.)
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v29.sql

BEGIN;

-- Garde-fou : la base doit etre exactement celle comptee le 17/10/2026, sinon rien n'est touche
DO $$
BEGIN
  IF (SELECT count(*) FROM annonce) <> 2
     OR (SELECT count(*) FROM rendez_vous WHERE annonce_id IS NOT NULL) <> 4
     OR (SELECT count(*) FROM rendez_vous WHERE annonce_id IS NOT NULL AND id NOT IN (6, 7, 8, 9)) <> 0
     OR (SELECT count(*) FROM facture WHERE rendez_vous_id IN (6, 7, 8, 9)) <> 2
     OR (SELECT count(*) FROM facture WHERE avoir_de_id IN (2, 3)) <> 0
     OR (SELECT count(*) FROM avis WHERE rendez_vous_id IN (6, 7, 8, 9)) <> 1
     OR (SELECT count(*) FROM avis_client WHERE rendez_vous_id IN (6, 7, 8, 9)) <> 0
     OR (SELECT count(*) FROM paiement WHERE rendez_vous_id IN (6, 7, 8, 9)) <> 0
     OR (SELECT count(*) FROM rendez_vous WHERE remplace_id IN (6, 7, 8, 9)) <> 0
     OR (SELECT count(*) FROM photo_annonce) <> 0
     OR (SELECT count(*) FROM signalement WHERE annonce_id IS NOT NULL) <> 0 THEN
    RAISE EXCEPTION 'La base a change depuis le 17/10/2026 : rien n''est efface, demander a Raphael.';
  END IF;
END $$;

-- 1. Les lignes de demonstration (accord de Raphael)
DELETE FROM ligne_facture WHERE facture_id IN (SELECT id FROM facture WHERE rendez_vous_id IN (6, 7, 8, 9));
DELETE FROM facture WHERE rendez_vous_id IN (6, 7, 8, 9);
DELETE FROM avis WHERE rendez_vous_id IN (6, 7, 8, 9);
DELETE FROM rendez_vous WHERE id IN (6, 7, 8, 9) AND annonce_id IS NOT NULL;
-- Les 2 demandes de devis (5 et 6) pointent vers l'annonce 16 : leur lien part avant l'annonce (elles restent)
ALTER TABLE demande_devis DROP COLUMN annonce_id;
DELETE FROM annonce WHERE id IN (15, 16);

-- 2. Un rendez-vous vient toujours d'une proposition
ALTER TABLE rendez_vous DROP CONSTRAINT rendez_vous_origine_connue;
ALTER TABLE rendez_vous DROP COLUMN annonce_id;
ALTER TABLE rendez_vous ALTER COLUMN proposition_id SET NOT NULL;

-- 3. Plus de lien vers une annonce (signalement ; demande_devis : fait plus haut)
ALTER TABLE signalement DROP COLUMN annonce_id;

-- 4. Les deux tables
DROP TABLE photo_annonce;
DROP TABLE annonce;

COMMIT;
