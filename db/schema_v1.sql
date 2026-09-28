-- rafals - schema_v1.sql (lot 0.2, 28/09/2026)
-- Cree le compte application "rafals_app" : lire et ecrire les donnees,
-- JAMAIS creer, modifier ou detruire une table. Aucune table creee ici.
-- Ne jamais modifier ce fichier une fois execute : une correction = schema_v2.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB" -v app_password="$RAFALS_APP_PASSWORD" -f -' < db/schema_v1.sql

CREATE ROLE rafals_app LOGIN PASSWORD :'app_password'
  NOSUPERUSER NOCREATEDB NOCREATEROLE;

-- Personne d'autre que l'administrateur ne cree d'objet dans la base
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON DATABASE rafals_db FROM PUBLIC;

-- Le compte application peut se connecter et utiliser le schema
GRANT CONNECT ON DATABASE rafals_db TO rafals_app;
GRANT USAGE ON SCHEMA public TO rafals_app;

-- Toute table creee plus tard par rafals_user sera lisible et modifiable
-- (lignes seulement) par rafals_app
ALTER DEFAULT PRIVILEGES FOR ROLE rafals_user IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO rafals_app;
ALTER DEFAULT PRIVILEGES FOR ROLE rafals_user IN SCHEMA public
  GRANT USAGE, SELECT ON SEQUENCES TO rafals_app;
