@echo off
rem Nettoie les donnees d'essai saisies a la main dans la vraie base
rem (sauvegarde d'abord, puis demande ton accord avant d'effacer)
cd /d %~dp0
if not exist db-sync\securite mkdir db-sync\securite
echo Sauvegarde de la base avant nettoyage...
docker compose exec -T db pg_dump -U rafals_user -d rafals_db --no-owner > db-sync\securite\avant-nettoyage.sql
if errorlevel 1 goto erreur
docker compose exec backend python -m scripts.nettoyer_donnees_test
pause
exit /b 0

:erreur
echo ERREUR : la sauvegarde a echoue, rien n'a ete nettoye.
pause
exit /b 1
