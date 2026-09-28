@echo off
rem Lance les boites Docker de rafals, puis ouvre la page dans le navigateur
cd /d %~dp0
docker compose up -d --build
echo.
echo Patiente quelques secondes, la page va s'ouvrir...
timeout /t 8 /nobreak > nul
start http://localhost:5174
