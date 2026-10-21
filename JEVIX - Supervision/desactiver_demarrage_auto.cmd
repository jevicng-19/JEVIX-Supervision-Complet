@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0desactiver_demarrage_auto.ps1"
if errorlevel 1 echo Echec de la desactivation du demarrage automatique.
pause
