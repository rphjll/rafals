-- rafals - schema_v28.sql (lot 8.7, 2e partie, 15/10/2026)
-- Notifications sur le telephone : la table APPAREIL.
-- Traduction du MLD valide par Raphael le 15/10/2026 (.doc/mld/MLD-notifications-appareil.html),
-- deja prevu dans le MLD du niveau 8 (.doc/mld/MLD-niveau-8-demandes.html).
-- Regles : RM-ALERTES.md, RM-APPLICATION.md (§ « Notifications sur l'appareil »).
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v29.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v28.sql

BEGIN;

-- Un telephone ou un ordinateur qui a accepte les notifications
CREATE TABLE appareil (
  id               bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id        bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  adresse          text        NOT NULL,
  cle_publique     text        NOT NULL,
  cle_secrete      text        NOT NULL,
  cree_le          timestamptz NOT NULL DEFAULT now(),
  dernier_envoi_le timestamptz,
  -- Un meme appareil n'est jamais enregistre deux fois
  CONSTRAINT appareil_adresse_unique UNIQUE (adresse)
);
CREATE INDEX appareil_compte_id_idx ON appareil (compte_id);

COMMIT;
