-- rafals - schema_v35.sql (niveau 14, 11/11/2026)
-- Le prix de l'heure de chaque metier d'un prestataire (comme la grande maquette : « 45 €/h » sur la carte).
-- Traduction du MLD valide par Raphael le 11/11/2026 (« oui » ; .doc/mld/MLD-prix-heure.html).
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v36.sql.
--
-- Execution (une seule fois par base, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v35.sql

BEGIN;

-- Le prix de l'heure du metier principal, en centimes (ex. 4500 = 45,00 €) ; vide tant que le prestataire ne l'a pas donne
ALTER TABLE prestataire
  ADD COLUMN metier_principal_prix_centimes integer
    CONSTRAINT prestataire_prix_heure_limites CHECK (metier_principal_prix_centimes BETWEEN 100 AND 100000);

-- Le prix de l'heure d'un metier secondaire, en centimes (ex. 5000 = 50,00 € comme plombier) ; vide tant qu'il n'est pas donne
ALTER TABLE metier_secondaire
  ADD COLUMN prix_centimes integer
    CONSTRAINT metier_secondaire_prix_heure_limites CHECK (prix_centimes BETWEEN 100 AND 100000);

COMMIT;
