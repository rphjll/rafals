@echo off
rem Charge (ou met a jour) la liste officielle des communes de France
rem depuis backend\app\donnees\communes.json.gz. Relancable sans risque : rien n'est supprime.
cd /d %~dp0
docker compose exec -T backend python -m scripts.charger_communes
if not "%1"=="auto" pause
