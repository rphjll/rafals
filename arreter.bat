@echo off
rem Arrete les boites Docker de rafals (les donnees de la base sont gardees)
cd /d %~dp0
docker compose down
