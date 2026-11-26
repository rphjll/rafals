@echo off
rem Lance rafals : ouvre Docker Desktop si besoin, demarre les boites Docker, puis ouvre la page.
rem Ne reconstruit PAS les boites (c'etait 5 a 20 minutes a chaque fois).
rem Apres un "git pull" ou un changement de requirements.txt / package.json : lancer installer.bat (il reconstruit).
cd /d %~dp0
setlocal enabledelayedexpansion

docker info > nul 2>&1
if not errorlevel 1 goto docker_pret
echo Ouverture de Docker Desktop...
start "" "C:\Program Files\Docker\Docker\Docker Desktop.exe"
set /a essais=0
:attendre_docker
timeout /t 3 /nobreak > nul
docker info > nul 2>&1
if not errorlevel 1 goto docker_pret
set /a essais+=1
if !essais! geq 60 (
  echo ERREUR : Docker Desktop ne repond pas apres 3 minutes. Ouvre-le a la main puis relance demarrer.bat.
  pause
  exit /b 1
)
goto attendre_docker
:docker_pret

echo Demarrage des boites Docker...
docker compose up -d
if errorlevel 1 (
  echo ERREUR : les boites n'ont pas demarre. Lis le message ci-dessus.
  pause
  exit /b 1
)

echo Attente du site...
set /a essais=0
:attendre_site
curl -s -o nul http://localhost:5174
if not errorlevel 1 goto site_pret
set /a essais+=1
if !essais! geq 60 goto site_pret
timeout /t 2 /nobreak > nul
goto attendre_site
:site_pret
start http://localhost:5174
