#!/bin/sh
# rafals - copie la STRUCTURE de la vraie base (tables, droits, sans aucune donnee)
# dans la base de test. Tourne DANS la boite "db", juste apres recreer_base.sh.
#   docker compose exec -T db sh -s < db/copier_structure_vers_test.sh
set -e
pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" --schema-only \
  | psql -q -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d rafals_test_db > /dev/null
echo "Structure de $POSTGRES_DB copiee dans rafals_test_db (aucune donnee)."
