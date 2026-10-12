-- rafals - schema_v26.sql (12/10/2026)
-- Limites d'un prestataire sans SIRET : le metier dit s'il demande un SIRET, le prestataire garde la date de sa case
-- « Mon activite est occasionnelle et je declare mes revenus aux impots ».
-- Traduction exacte du MLD valide par Raphael le 09/10/2026 (.doc/mld/MLD-limites-sans-siret.html).
-- Regles : RM-PRESTATAIRES.md (§ « Limites d'un prestataire sans SIRET »), RM-METIERS-SANS-SIRET.md.
-- AJOUTS SEULEMENT : aucune table nouvelle, aucune suppression. Ne jamais modifier ce fichier une fois execute :
-- une correction = schema_v27.sql.
--
-- Execution (une seule fois, par le compte administrateur rafals_user) :
--   docker compose exec -T db sh -c 'psql -v ON_ERROR_STOP=1 -U "$POSTGRES_USER" -d "$POSTGRES_DB"' < db/schema_v26.sql

BEGIN;

-- Tout metier demande un SIRET au depart (donc aussi un metier ajoute plus tard) ...
ALTER TABLE metier ADD COLUMN siret_obligatoire boolean NOT NULL DEFAULT true;
COMMENT ON COLUMN metier.siret_obligatoire IS 'Oui : un prestataire sans SIRET verifie ne peut pas repondre aux demandes de ce metier (RM-METIERS-SANS-SIRET).';
-- ... puis les 50 metiers « autorises sans SIRET » de RM-METIERS-SANS-SIRET.md (reconnus par leur code)
UPDATE metier SET siret_obligatoire = false WHERE code IN (
  'aide-devoirs',
  'animateur-enfants',
  'community-manager',
  'conciergerie',
  'cordonnier',
  'cours-couture',
  'cours-cuisine',
  'cours-dessin',
  'cours-informatique',
  'cours-langues',
  'cours-musique',
  'courses',
  'debarras',
  'decoration-evenements',
  'depannage-informatique',
  'developpeur-web',
  'dj',
  'ecrivain-public',
  'fleuriste-evenements',
  'formateur',
  'garde-enfants',
  'grand-nettoyage',
  'graphiste',
  'horloger',
  'jardinier',
  'lavage-auto',
  'location-fete',
  'magicien',
  'menage',
  'montage-meubles',
  'multiservices',
  'musicien',
  'nettoyage-textiles',
  'pet-sitter',
  'photographe',
  'promeneur-chiens',
  'redacteur',
  'relooking',
  'reparation-electromenager',
  'reparation-telephone',
  'repassage',
  'retouches',
  'secretariat',
  'soutien-scolaire',
  'taille-haies',
  'toiletteur',
  'traducteur',
  'videaste',
  'vitres',
  'wedding-planner'
);

ALTER TABLE prestataire ADD COLUMN activite_occasionnelle_le timestamptz;
COMMENT ON COLUMN prestataire.activite_occasionnelle_le IS 'Date ou il a coche « Mon activite est occasionnelle et je declare mes revenus aux impots » ; vide : pas encore cochee.';

COMMIT;
