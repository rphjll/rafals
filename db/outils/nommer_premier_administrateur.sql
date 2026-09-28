-- rafals - nomme le PREMIER administrateur (lance par nommer-premier-administrateur.bat).
-- Refuse s'il existe deja un administrateur : les suivants se nomment depuis l'ecran Administration.
-- Variable psql attendue : email

SELECT count(*) > 0 AS deja_un_admin FROM compte WHERE est_administrateur \gset
\if :deja_un_admin
  \echo 'Il y a deja un administrateur : les suivants se nomment depuis l ecran Administration de rafals.'
  \quit
\endif

WITH cible AS (
  UPDATE compte SET est_administrateur = true
  WHERE email = lower(trim(:'email'))
  RETURNING id
)
INSERT INTO journal_action (auteur_id, action, table_cible, ligne_id, avant, apres)
SELECT NULL, 'nommer_premier_administrateur', 'compte', id,
       '{"est_administrateur": false}', '{"est_administrateur": true}'
FROM cible;

SELECT count(*) > 0 AS fait FROM compte WHERE email = lower(trim(:'email')) AND est_administrateur \gset
\if :fait
  \echo 'C est fait : ce compte est administrateur de rafals.'
\else
  \echo 'Aucun compte avec cette adresse : cree d abord ton compte dans rafals, puis relance.'
\endif
