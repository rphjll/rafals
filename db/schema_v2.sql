-- rafals - schema_v2.sql (lot 1.1, 28/09/2026)
-- Tables des comptes et de la connexion. Traduction exacte du MLD valide par Raphael
-- le 28/09/2026 (.doc/mld/MLD-lot-1.1-comptes.html). Regles : RM-COMPTES.md, RM-CLIENTS.md.
-- Ne jamais modifier ce fichier une fois execute : une correction = schema_v3.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v2.sql
-- Le compte application rafals_app recoit automatiquement le droit de lire et ecrire
-- les lignes (droits par defaut poses par schema_v1.sql).

BEGIN;

CREATE TABLE compte (
  id                    bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  email                 text        NOT NULL,
  mot_de_passe_hache    text        NOT NULL,
  prenom                text        NOT NULL,
  nom                   text        NOT NULL,
  telephone             text        NOT NULL,
  date_naissance        date        NOT NULL,
  email_verifie_le      timestamptz,
  echecs_connexion      integer     NOT NULL DEFAULT 0,
  bloque_jusqu_au       timestamptz,
  derniere_connexion_le timestamptz,
  cree_le               timestamptz NOT NULL DEFAULT now(),
  CONSTRAINT compte_email_unique UNIQUE (email),
  CONSTRAINT compte_email_minuscules CHECK (email = lower(email)),
  CONSTRAINT compte_echecs_positifs CHECK (echecs_connexion >= 0)
);
COMMENT ON TABLE compte IS 'Une personne inscrite sur rafals (cliente, prestataire, ou les deux).';
COMMENT ON COLUMN compte.mot_de_passe_hache IS 'Mot de passe brouille (argon2), jamais lisible.';
COMMENT ON COLUMN compte.email_verifie_le IS 'Date du clic sur le lien de verification ; vide = pas encore verifie.';
COMMENT ON COLUMN compte.echecs_connexion IS 'Mauvais mots de passe de suite ; remis a 0 apres une connexion reussie.';
COMMENT ON COLUMN compte.bloque_jusqu_au IS 'Fin du blocage apres 5 erreurs ; vide = pas bloque.';

CREATE TABLE session (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id   bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  jeton_hache text        NOT NULL,
  appareil    text,
  cree_le     timestamptz NOT NULL DEFAULT now(),
  expire_le   timestamptz NOT NULL,
  fermee_le   timestamptz,
  CONSTRAINT session_jeton_unique UNIQUE (jeton_hache)
);
CREATE INDEX session_compte_id_idx ON session (compte_id);
COMMENT ON TABLE session IS 'Un appareil connecte a un compte (rester connecte 30 jours).';
COMMENT ON COLUMN session.fermee_le IS 'Clic sur Se deconnecter ; vide = session active.';

CREATE TABLE jeton_mail (
  id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id   bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  usage       text        NOT NULL,
  jeton_hache text        NOT NULL,
  cree_le     timestamptz NOT NULL DEFAULT now(),
  expire_le   timestamptz NOT NULL,
  utilise_le  timestamptz,
  CONSTRAINT jeton_mail_jeton_unique UNIQUE (jeton_hache),
  CONSTRAINT jeton_mail_usage_connu CHECK (usage IN ('verification', 'mot_de_passe'))
);
CREATE INDEX jeton_mail_compte_id_idx ON jeton_mail (compte_id);
COMMENT ON TABLE jeton_mail IS 'Lien envoye par mail (verification d''adresse ou mot de passe oublie), utilisable une seule fois.';

COMMIT;
