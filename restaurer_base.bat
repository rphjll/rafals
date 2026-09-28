@echo off
rem Remplace la base locale rafals_db par la derniere sauvegarde db-sync\donnees.sql
rem (copie de securite d'abord, et seulement si tu tapes OUI)
cd /d %~dp0
if not exist db-sync\donnees.sql (
  echo Aucune sauvegarde trouvee : db-sync\donnees.sql n'existe pas. Rien n'a ete touche.
  pause
  exit /b 1
)
echo ATTENTION : ta base locale rafals_db va etre REMPLACEE par db-sync\donnees.sql
set /p rep="Tape OUI (en majuscules) pour continuer : "
if not "%rep%"=="OUI" (
  echo Annule : rien n'a ete touche.
  pause
  exit /b 0
)
if not exist db-sync\securite mkdir db-sync\securite
echo Copie de securite de la base actuelle dans db-sync\securite\avant-restauration.sql...
docker compose exec -T db pg_dump -U rafals_user -d rafals_db --no-owner > db-sync\securite\avant-restauration.sql
if errorlevel 1 goto erreur
docker compose stop backend
docker compose exec -T -e BASE_CIBLE=rafals_db db sh -s < db\recreer_base.sh
if errorlevel 1 goto erreur
docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U rafals_user -d rafals_db < db-sync\donnees.sql
if errorlevel 1 goto erreur
docker compose start backend
echo Base restauree.
pause
exit /b 0

:erreur
echo ERREUR : restauration interrompue. La copie de securite est dans db-sync\securite\avant-restauration.sql
docker compose start backend
pause
exit /b 1
