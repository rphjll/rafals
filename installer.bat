@echo off
rem rafals - installation complete sur un nouveau PC, en un clic.
rem A faire avant : installer Docker Desktop et le lancer (la baleine doit etre visible en bas a droite).
rem Relancable sans risque : ce qui est deja fait est garde, rien n'est efface.
cd /d %~dp0
setlocal enabledelayedexpansion

echo ============================================
echo   Installation de rafals
echo ============================================
echo.

echo [1/7] Docker est-il lance ?
docker info > nul 2>&1
if errorlevel 1 (
  echo ERREUR : Docker Desktop n'est pas lance. Ouvre-le, attends que la baleine soit verte, puis relance installer.bat.
  pause
  exit /b 1
)

echo [2/7] Fichier des reglages .env...
powershell -NoProfile -ExecutionPolicy Bypass -File outils-installation\creer-env.ps1
if errorlevel 1 goto erreur

echo [3/7] Construction et demarrage des boites Docker (la premiere fois : 10 a 20 minutes)...
docker compose up -d --build
if errorlevel 1 goto erreur

echo [4/7] Attente de la base de donnees...
set /a essais=0
:attendre_base
docker compose exec -T db sh -c "pg_isready -U $POSTGRES_USER -d $POSTGRES_DB" > nul 2>&1
if not errorlevel 1 goto base_prete
set /a essais+=1
if !essais! geq 60 goto erreur
timeout /t 2 /nobreak > nul
goto attendre_base
:base_prete

echo [5/7] Tables de la base (fichiers db\schema_v1.sql, v2, v3... dans l'ordre)...
docker compose exec -T db sh -c "psql -U $POSTGRES_USER -d $POSTGRES_DB -tAc \"SELECT to_regclass('public.compte') IS NOT NULL\"" > "%TEMP%\rafals_base.txt"
set /p deja=< "%TEMP%\rafals_base.txt"
if "!deja!"=="t" (
  echo     La base a deja ses tables : rien a faire.
) else (
  for /l %%i in (1,1,200) do (
    if exist db\schema_v%%i.sql (
      echo     schema_v%%i.sql
      docker compose exec -T db sh -c "psql -q -v ON_ERROR_STOP=1 -U $POSTGRES_USER -d $POSTGRES_DB -v app_password=$RAFALS_APP_PASSWORD -f -" < db\schema_v%%i.sql > nul
      if errorlevel 1 goto erreur
    )
  )
)

echo [6/7] Placard a fichiers (Garage)...
call preparer-stockage.bat auto

echo [7/7] Listes de depart : communes de France, metiers, mots interdits...
docker compose restart backend > nul
timeout /t 8 /nobreak > nul
call charger-communes.bat auto
call charger-metiers.bat auto
call charger-mots-interdits.bat auto

echo.
echo ============================================
echo   rafals est installe.
echo   - Le site       : http://localhost:5174
echo   - Les mails     : http://localhost:8025 (rien ne part pour de vrai)
echo   Ensuite : cree ton compte sur le site, puis lance
echo   nommer-premier-administrateur.bat pour devenir administrateur.
echo   Les fois suivantes : demarrer.bat suffit.
echo ============================================
start http://localhost:5174
pause
exit /b 0

:erreur
echo.
echo ERREUR : l'installation s'est arretee a l'etape ci-dessus. Lis le message, puis relance installer.bat
echo (ce qui est deja fait sera garde).
pause
exit /b 1
