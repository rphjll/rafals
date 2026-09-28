#!/bin/sh
# rafals - efface puis recree une base VIDE, avec les droits du compte application.
# Tourne DANS la boite "db". Utilise par lancer-tests.bat (base de test)
# et restaurer_base.bat (base principale, apres accord de Raphael).
#   docker compose exec -T -e BASE_CIBLE=rafals_test_db db sh -s < db/recreer_base.sh
set -e

if [ -z "$BASE_CIBLE" ]; then
  echo "STOP : BASE_CIBLE n'est pas precisee, rien n'a ete touche." >&2
  exit 1
fi

# Le compte application existe au niveau du serveur de bases (cree par schema_v1.sql).
# Sur un PC neuf, il n'existe pas encore : on le cree avec le mot de passe du fichier .env.
if [ "$(psql -U "$POSTGRES_USER" -d postgres -tAc "SELECT 1 FROM pg_roles WHERE rolname = '$RAFALS_APP_USER'")" != "1" ]; then
  psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres \
    -v app_user="$RAFALS_APP_USER" -v app_password="$RAFALS_APP_PASSWORD" \
    -c "CREATE ROLE :\"app_user\" LOGIN PASSWORD :'app_password' NOSUPERUSER NOCREATEDB NOCREATEROLE;"
fi

psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d postgres <<SQL
DROP DATABASE IF EXISTS "$BASE_CIBLE" WITH (FORCE);
CREATE DATABASE "$BASE_CIBLE";
REVOKE ALL ON DATABASE "$BASE_CIBLE" FROM PUBLIC;
GRANT CONNECT ON DATABASE "$BASE_CIBLE" TO "$RAFALS_APP_USER";
SQL

psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$BASE_CIBLE" <<SQL
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
GRANT USAGE ON SCHEMA public TO "$RAFALS_APP_USER";
SQL

echo "Base $BASE_CIBLE recreee (vide)."
