@echo off
rem Copie la base dans db-sync, puis sauvegarde dans git et envoie sur GitHub
cd /d %~dp0
if not exist db-sync mkdir db-sync
docker compose exec -T db pg_dump -U rafals_user -d rafals_db --no-owner > db-sync\donnees.sql
set /p msg="Decris en quelques mots ce que tu as fait : "
if "%msg%"=="" set msg=Sauvegarde du %date%
git add -A
git commit -m "%msg%"
git push
pause
