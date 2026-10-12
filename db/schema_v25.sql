-- rafals - schema_v25.sql (08/10/2026)
-- Lot 9.1, suite de schema_v24.sql : les ajouts qui restaient du MLD valide par Raphael le 04/10/2026
-- (.doc/mld/MLD-retrait-annonces.html). AJOUTS SEULEMENT : rien n'est supprime (les suppressions sont au lot 9.4).
--   PRESTATAIRE.lieu : ou a lieu le service (c'etait ecrit sur chaque annonce).
--   DEMANDE_DEVIS.metier_id : le metier concerne (avant : lu dans l'annonce) ; annonce_id devient facultative.
--   DEMANDE_DEVIS.demande_id : la demande publiee par le client, s'il y en a une.
-- Regles : RM-PRESTATAIRES.md § « Sans annonces », RM-DEVIS.md. Ne jamais modifier ce fichier une fois execute :
-- une correction = schema_v26.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v25.sql

BEGIN;

-- Le lieu du service passe dans le profil ; les profils existants partent sur « chez le client »
ALTER TABLE prestataire ADD COLUMN lieu text NOT NULL DEFAULT 'chez_client';
ALTER TABLE prestataire ADD CONSTRAINT prestataire_lieu_connu CHECK (lieu IN ('chez_client', 'chez_moi', 'les_deux'));
COMMENT ON COLUMN prestataire.lieu IS 'Ou a lieu le service : chez_client, chez_moi (son adresse) ou les_deux. Le lieu exact de chaque rendez-vous reste ecrit dans la proposition.';

-- Une demande de devis porte son metier (recopie de l'annonce pour les lignes existantes)
ALTER TABLE demande_devis ADD COLUMN metier_id bigint REFERENCES metier (id) ON DELETE RESTRICT;
UPDATE demande_devis d SET metier_id = a.metier_id FROM annonce a WHERE a.id = d.annonce_id;
ALTER TABLE demande_devis ALTER COLUMN metier_id SET NOT NULL;
ALTER TABLE demande_devis ALTER COLUMN annonce_id DROP NOT NULL;
CREATE INDEX demande_devis_metier_id_idx ON demande_devis (metier_id);
COMMENT ON COLUMN demande_devis.metier_id IS 'Le metier concerne par le devis : celui de l''annonce (recopie) ou celui choisi sur le profil du prestataire.';

-- Une demande de devis peut venir d'une demande publiee par le client
ALTER TABLE demande_devis ADD COLUMN demande_id bigint REFERENCES demande (id) ON DELETE RESTRICT;
CREATE INDEX demande_devis_demande_id_idx ON demande_devis (demande_id);
COMMENT ON COLUMN demande_devis.demande_id IS 'La demande publiee par le client dont vient ce devis (vide s''il a ecrit depuis une annonce ou un profil).';

COMMIT;
