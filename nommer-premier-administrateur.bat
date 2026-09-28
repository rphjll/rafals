@echo off
rem Nomme le PREMIER administrateur de rafals (une seule fois).
rem Cree d'abord ton vrai compte dans rafals, puis lance ce fichier.
cd /d %~dp0
set /p email="Adresse mail de ton compte rafals : "
if "%email%"=="" (
  echo Aucune adresse : rien n'a ete fait.
  pause
  exit /b 1
)
docker compose exec -T db psql -q -v ON_ERROR_STOP=1 -U rafals_user -d rafals_db -v email="%email%" -f - < db\outils\nommer_premier_administrateur.sql
pause
