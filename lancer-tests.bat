@echo off
rem Lance les tests automatiques sur la base de test rafals_test_db (jamais sur la vraie base)
cd /d %~dp0
echo [1/3] Base de test : effacement et recreation...
docker compose exec -T -e BASE_CIBLE=rafals_test_db db sh -s < db\recreer_base.sh
if errorlevel 1 goto erreur
echo [2/3] Base de test : copie de la structure de la vraie base...
docker compose exec -T db sh -s < db\copier_structure_vers_test.sh
if errorlevel 1 goto erreur
echo [3/3] Tests...
docker compose exec -T -e POSTGRES_DB=rafals_test_db backend pytest -v
pause
exit /b 0

:erreur
echo ERREUR : la base de test n'a pas pu etre preparee. Les tests n'ont pas ete lances.
pause
exit /b 1
