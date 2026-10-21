@echo off
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0activer_demarrage_auto.ps1"
if errorlevel 1 echo Echec de l'activation du demarrage automatique.
pause
