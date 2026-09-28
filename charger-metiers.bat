@echo off
rem Charge (ou met a jour) la liste des dossiers et des metiers de rafals
rem depuis backend\app\donnees\metiers.json. Relancable sans risque : rien n'est supprime.
cd /d %~dp0
docker compose exec -T backend python -m scripts.charger_metiers
pause
