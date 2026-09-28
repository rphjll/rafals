@echo off
rem Prepare le placard a fichiers Garage : a lancer UNE SEULE FOIS par PC
rem (apres le premier demarrer.bat). Lit les cles dans le fichier .env.
cd /d %~dp0
docker compose up -d garage
timeout /t 4 /nobreak > nul

set NOEUD=
for /f "tokens=1 delims=@" %%i in ('docker compose exec -T garage /garage node id -q 2^>nul') do set NOEUD=%%i
if "%NOEUD%"=="" goto erreur

for /f "usebackq tokens=1,* delims==" %%a in (".env") do (
  if "%%a"=="S3_CLE_ACCES" set CLE=%%b
  if "%%a"=="S3_CLE_SECRETE" set SECRET=%%b
  if "%%a"=="S3_COMPARTIMENT" set COMPARTIMENT=%%b
)

echo [1/4] Rangement du placard...
docker compose exec -T garage /garage layout assign -z pc -c 10G %NOEUD% 2> nul
docker compose exec -T garage /garage layout apply --version 1 2> nul
echo [2/4] Creation du compartiment %COMPARTIMENT%...
docker compose exec -T garage /garage bucket create %COMPARTIMENT% 2> nul
echo [3/4] Cle d'acces de rafals...
docker compose exec -T garage /garage key import --yes -n rafals %CLE% %SECRET% 2> nul
echo [4/4] Droits de rafals sur le compartiment...
docker compose exec -T garage /garage bucket allow --read --write --owner %COMPARTIMENT% --key %CLE% 2> nul
echo [+] Compartiment des tests automatiques (rafals-test, vide a chaque lancement des tests)...
docker compose exec -T garage /garage bucket create rafals-test 2> nul
docker compose exec -T garage /garage bucket allow --read --write --owner rafals-test --key %CLE% 2> nul
echo.
echo Stockage pret.
pause
exit /b 0

:erreur
echo ERREUR : Garage ne repond pas. Lance d'abord demarrer.bat, puis reessaie.
pause
exit /b 1
