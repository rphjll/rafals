-- rafals - schema_v33.sql (suite du lot 10.4, 22/10/2026)
-- Personnaliser la carte de visite : la couleur choisie et la petite phrase, gardees d'une visite a l'autre.
-- Traduction du MLD valide par Raphael le 22/10/2026 (« oui » ; .doc/mld/MLD-carte-visite.html).
-- AJOUTS SEULEMENT : rien n'est supprime. Ne jamais modifier ce fichier une fois execute : une correction = schema_v34.sql.
--
-- Execution (une seule fois par base, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v33.sql

BEGIN;

-- La couleur de la carte, une des 6 toutes pretes (vert au depart : la carte d'avant)
-- (ex. Karim : bleu-nuit ; Lea, qui n'a rien change : vert)
ALTER TABLE prestataire
  ADD COLUMN carte_couleur text NOT NULL DEFAULT 'vert'
    CONSTRAINT prestataire_carte_couleur_connue CHECK (carte_couleur IN ('vert', 'bleu-nuit', 'orange', 'bordeaux', 'violet', 'noir')),
  -- La petite phrase sous la ville, 40 caracteres au plus ; vide = pas de phrase
  -- (ex. « Devis gratuit, intervention sous 48 h »)
  ADD COLUMN carte_phrase text
    CONSTRAINT prestataire_carte_phrase_courte CHECK (char_length(carte_phrase) BETWEEN 1 AND 40);

COMMIT;
