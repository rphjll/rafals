-- rafals - schema_v21.sql (lot 8.1, 04/10/2026)
-- Messagerie : une conversation par couple client / prestataire, ses messages, leurs photos ;
-- signalement d'une conversation.
-- Traduction du MLD valide par Raphael le 04/10/2026 (.doc/mld/MLD-niveau-8-demandes.html), partie « lot 8.1 »
-- + la partie « conversation » de SIGNALEMENT (le reste de SIGNALEMENT, les demandes, vient au lot 8.3).
-- Regles : RM-MESSAGERIE.md. Ne jamais modifier ce fichier une fois execute : une correction = schema_v22.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v21.sql

BEGIN;

CREATE TABLE conversation (
  id                 bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  client_id          bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  prestataire_id     bigint      NOT NULL REFERENCES prestataire (id) ON DELETE RESTRICT,
  bloquee_par_id     bigint      REFERENCES compte (id) ON DELETE RESTRICT,
  cree_le            timestamptz NOT NULL DEFAULT now(),
  dernier_message_le timestamptz NOT NULL DEFAULT now(),
  client_lu_le       timestamptz,
  prestataire_lu_le  timestamptz,
  bloquee_le         timestamptz,
  CONSTRAINT conversation_une_par_couple UNIQUE (client_id, prestataire_id),
  -- Bloquee : une date et son auteur, ensemble
  CONSTRAINT conversation_blocage_coherent CHECK ((bloquee_le IS NULL) = (bloquee_par_id IS NULL))
);
CREATE INDEX conversation_prestataire_id_idx ON conversation (prestataire_id);
COMMENT ON TABLE conversation IS 'Messages prives entre un client et un prestataire : une seule conversation par couple (RM-MESSAGERIE).';
COMMENT ON COLUMN conversation.client_lu_le IS 'Le client a lu tous les messages jusqu''a ce moment (compteur rouge, « lu »).';
COMMENT ON COLUMN conversation.dernier_message_le IS 'Pour trier la liste ; sans message depuis 3 ans, la conversation est effacee.';

CREATE TABLE message (
  id              bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  conversation_id bigint      NOT NULL REFERENCES conversation (id) ON DELETE RESTRICT,
  auteur_id       bigint      NOT NULL REFERENCES compte (id) ON DELETE RESTRICT,
  texte           text        NOT NULL,
  genre           text        NOT NULL DEFAULT 'texte',
  cree_le         timestamptz NOT NULL DEFAULT now(),
  mail_envoye_le  timestamptz,
  CONSTRAINT message_genre_connu CHECK (genre IN ('texte', 'information')),
  CONSTRAINT message_texte_longueur CHECK (length(texte) <= 2000)
);
CREATE INDEX message_conversation_id_idx ON message (conversation_id, cree_le);
COMMENT ON TABLE message IS 'Un message d''une conversation. Le texte est garde tel qu''ecrit : les coordonnees sont masquees a l''affichage tant qu''il n''y a pas de rendez-vous entre les deux.';
COMMENT ON COLUMN message.genre IS 'texte = ecrit par une personne ; information = ecrit par rafals (ex. « Marie D. a refuse la proposition »).';
COMMENT ON COLUMN message.mail_envoye_le IS 'Le mail « Karim vous a ecrit » est parti (message pas lu au bout de 15 minutes).';

CREATE TABLE photo_message (
  id         bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
  message_id bigint  NOT NULL REFERENCES message (id) ON DELETE RESTRICT,
  fichier_id bigint  NOT NULL REFERENCES fichier (id) ON DELETE RESTRICT,
  ordre      integer NOT NULL,
  CONSTRAINT photo_message_fichier_unique UNIQUE (fichier_id),
  CONSTRAINT photo_message_ordre_unique UNIQUE (message_id, ordre),
  CONSTRAINT photo_message_ordre_valide CHECK (ordre BETWEEN 1 AND 5)
);
COMMENT ON TABLE photo_message IS 'Photo jointe a un message (5 au plus).';

-- Signaler une conversation : la personne visee peut etre le client (pas de prestataire vise)
ALTER TABLE signalement ADD COLUMN conversation_id bigint REFERENCES conversation (id) ON DELETE RESTRICT;
ALTER TABLE signalement ALTER COLUMN prestataire_id DROP NOT NULL;
ALTER TABLE signalement ADD CONSTRAINT signalement_cible_connue CHECK (prestataire_id IS NOT NULL OR conversation_id IS NOT NULL);
CREATE INDEX signalement_conversation_id_idx ON signalement (conversation_id);
COMMENT ON COLUMN signalement.conversation_id IS 'Conversation signalee : l''administrateur a alors le droit de la lire (RM-MESSAGERIE).';

COMMIT;
