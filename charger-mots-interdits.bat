@echo off
rem Charge la liste de depart des mots interdits dans les avis (fichier backend/app/donnees/mots_interdits.json).
rem Relancable sans risque : un mot deja present est ignore, rien n'est supprime.
cd /d %~dp0
docker compose exec -T backend python -m scripts.charger_mots_interdits
pause
