-- rafals - schema_v34.sql (lot 13.1, 09/11/2026)
-- « Un probleme ? Une idee ? » : la table RETOUR (les messages des utilisateurs, lus chaque soir par la routine).
-- Traduction du MLD valide par Raphael le 09/11/2026 (« oui » ; .doc/mld/MLD-lot-13.1-retours.html). Regle : .doc/regles-metier/RM-RETOURS.md.
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v35.sql.
--
-- Execution (une seule fois par base, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v34.sql

BEGIN;

-- Un message envoye par un compte connecte
-- (ex. Julie : probleme, « Le bouton Publier ne repond pas sur mon telephone », /demandes/nouvelle, telephone, « Chrome sur Android », capture n° 87)
CREATE TABLE retour (
  id          bigint      GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  auteur_id   bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  -- La capture d'ecran, facultative ; effacer le fichier vide la case toute seule
  fichier_id  bigint      REFERENCES fichier (id) ON DELETE SET NULL,
  -- Le choix de l'utilisateur, garde tel quel (la routine notera sa correction ailleurs, lot 13.2)
  sorte       text        NOT NULL CONSTRAINT retour_sorte_connue CHECK (sorte IN ('probleme', 'idee')),
  texte       text        NOT NULL CONSTRAINT retour_texte_longueur CHECK (char_length(texte) BETWEEN 10 AND 2000),
  -- Ajoutes tout seuls a l'envoi
  page        text        NOT NULL,                                   -- ex. /demandes/nouvelle
  appareil    text        NOT NULL CONSTRAINT retour_appareil_connu CHECK (appareil IN ('telephone', 'ordinateur')),
  navigateur  text        NOT NULL,                                   -- ex. Chrome sur Android
  -- a_traiter : la routine le lira ; injurieux : garde pour l'administrateur, jamais lu par la routine
  statut      text        NOT NULL DEFAULT 'a_traiter' CONSTRAINT retour_statut_connu CHECK (statut IN ('a_traiter', 'injurieux')),
  cree_le     timestamptz NOT NULL DEFAULT now(),
  -- Une capture ne sert qu'a un seul message
  CONSTRAINT retour_fichier_unique UNIQUE (fichier_id)
);
-- Compter les messages d'un compte depuis minuit (limite de 5 par jour)
CREATE INDEX retour_auteur_cree_le_idx ON retour (auteur_id, cree_le);
-- La routine du soir cherche les messages a traiter
CREATE INDEX retour_statut_idx ON retour (statut);

COMMIT;
