-- rafals - schema_v18.sql (lot 7.1, 04/10/2026)
-- Creer une auto-entreprise depuis rafals : le dossier de creation et ses papiers.
-- Traduction exacte du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-lot-7.1-creation-auto-entreprise.html).
-- Regles : RM-CREATION-AUTO-ENTREPRISE.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v19.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v18.sql

BEGIN;

CREATE TABLE dossier_creation (
  id                     bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  compte_id              bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  metier_id              bigint      REFERENCES metier (id) ON DELETE RESTRICT,
  commune_id             bigint      REFERENCES commune (id) ON DELETE RESTRICT,
  naissance_commune_id   bigint      REFERENCES commune (id) ON DELETE RESTRICT,
  -- Etape 1 « Vous » (tout est facultatif tant que le dossier est un brouillon)
  civilite               text,
  nom_naissance          text,
  nom_usage              text,
  prenoms                text,
  naissance_le           date,
  naissance_pays         text,
  nationalite            text,
  situation_famille      text,
  numero_secu            text,
  adresse_rue            text,
  mail                   text,
  telephone              text,
  pere_nom               text,
  mere_nom               text,
  -- Etape 2 « Votre activite »
  description            text,
  debut_le               date,
  lieu_travail           text,
  local_adresse          text,
  nom_commercial         text,
  activite_en_meme_temps text,
  ancien_siren           text,
  -- Etape 3 « Vos choix »
  periodicite            text,
  impot_avec_cotisations boolean,
  acre_demandee          boolean,
  adresse_non_publique   boolean,
  -- Envoi et suivi
  statut                 text        NOT NULL DEFAULT 'brouillon',
  cree_le                timestamptz NOT NULL DEFAULT now(),
  modifie_le             timestamptz NOT NULL DEFAULT now(),
  statut_change_le       timestamptz NOT NULL DEFAULT now(),
  certifie_le            timestamptz,
  pouvoir_le             timestamptz,
  pouvoir_texte          text,
  envoye_le              timestamptz,
  guichet_id             text,
  guichet_numero         text,
  motif                  text,
  corriger_avant_le      date,
  siret_recu             text,
  sensible_efface_le     timestamptz,
  CONSTRAINT dossier_creation_statut_connu CHECK (statut IN ('brouillon', 'envoye', 'en_examen', 'a_corriger', 'accepte', 'refuse', 'ferme')),
  CONSTRAINT dossier_creation_civilite_connue CHECK (civilite IS NULL OR civilite IN ('monsieur', 'madame')),
  CONSTRAINT dossier_creation_nationalite_connue CHECK (nationalite IS NULL OR nationalite IN ('francaise', 'union_europeenne', 'autre')),
  CONSTRAINT dossier_creation_situation_connue CHECK (situation_famille IS NULL OR situation_famille IN ('celibataire', 'concubinage', 'pacse', 'marie', 'divorce', 'veuf')),
  CONSTRAINT dossier_creation_lieu_travail_connu CHECK (lieu_travail IS NULL OR lieu_travail IN ('chez_clients', 'chez_moi', 'local')),
  CONSTRAINT dossier_creation_activite_connue CHECK (activite_en_meme_temps IS NULL OR activite_en_meme_temps IN ('aucune', 'salarie', 'retraite')),
  CONSTRAINT dossier_creation_periodicite_connue CHECK (periodicite IS NULL OR periodicite IN ('mois', 'trimestre')),
  CONSTRAINT dossier_creation_numero_secu_format CHECK (numero_secu IS NULL OR numero_secu ~ '^[0-9]{15}$'),
  CONSTRAINT dossier_creation_ancien_siren_format CHECK (ancien_siren IS NULL OR ancien_siren ~ '^[0-9]{9}$'),
  CONSTRAINT dossier_creation_siret_recu_format CHECK (siret_recu IS NULL OR siret_recu ~ '^[0-9]{14}$'),
  CONSTRAINT dossier_creation_description_longueur CHECK (description IS NULL OR length(description) BETWEEN 10 AND 250),
  -- Ne a l'etranger (un pays) ou en France (une commune), jamais les deux
  CONSTRAINT dossier_creation_naissance_un_seul_lieu CHECK (naissance_pays IS NULL OR naissance_commune_id IS NULL),
  -- Envoye : la date d'envoi, les deux cases cochees et le texte du pouvoir, ensemble
  CONSTRAINT dossier_creation_envoi_coherent CHECK ((statut = 'brouillon') = (envoye_le IS NULL)
                                                    AND (envoye_le IS NULL OR (certifie_le IS NOT NULL AND pouvoir_le IS NOT NULL AND pouvoir_texte IS NOT NULL))),
  -- Accepte : le SIRET est connu
  CONSTRAINT dossier_creation_accepte_coherent CHECK ((statut = 'accepte') = (siret_recu IS NOT NULL)),
  -- Une fois les donnees sensibles effacees, elles sont vraiment vides
  CONSTRAINT dossier_creation_sensible_efface CHECK (sensible_efface_le IS NULL
                                                     OR (numero_secu IS NULL AND pere_nom IS NULL AND mere_nom IS NULL))
);
CREATE INDEX dossier_creation_compte_id_idx ON dossier_creation (compte_id);
-- Un seul dossier ouvert par compte
CREATE UNIQUE INDEX dossier_creation_un_seul_ouvert ON dossier_creation (compte_id)
  WHERE statut IN ('brouillon', 'envoye', 'en_examen', 'a_corriger');
COMMENT ON TABLE dossier_creation IS 'Dossier de creation d''auto-entreprise envoye par rafals au guichet de l''Etat (RM-CREATION-AUTO-ENTREPRISE). Lie au compte, pas au profil de prestataire.';
COMMENT ON COLUMN dossier_creation.numero_secu IS 'Sensible : vide des que le dossier est accepte, refuse ou ferme (sensible_efface_le).';
COMMENT ON COLUMN dossier_creation.pouvoir_texte IS 'Le pouvoir donne a rafals, mot pour mot, tel que la personne l''a accepte.';

CREATE TABLE piece_dossier (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  dossier_id bigint      NOT NULL REFERENCES dossier_creation (id) ON DELETE RESTRICT,
  fichier_id bigint      REFERENCES fichier (id) ON DELETE RESTRICT,
  sorte      text        NOT NULL,
  depose_le  timestamptz NOT NULL DEFAULT now(),
  a_refaire  boolean     NOT NULL DEFAULT false,
  efface_le  timestamptz,
  CONSTRAINT piece_dossier_sorte_connue CHECK (sorte IN ('identite', 'titre_sejour', 'diplome', 'attestation', 'pouvoir', 'autorisation_parents', 'bail')),
  CONSTRAINT piece_dossier_fichier_unique UNIQUE (fichier_id),
  -- Le fichier est la tant que la piece n'est pas effacee, et plus apres
  CONSTRAINT piece_dossier_efface_coherent CHECK ((efface_le IS NULL) = (fichier_id IS NOT NULL))
);
CREATE INDEX piece_dossier_dossier_id_idx ON piece_dossier (dossier_id);
COMMENT ON TABLE piece_dossier IS 'Un papier d''un dossier de creation (piece d''identite, diplome...). Le fichier est efface a la fin du dossier ; la ligne reste.';

COMMIT;
