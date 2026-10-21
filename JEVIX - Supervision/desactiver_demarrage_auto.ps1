$ErrorActionPreference = 'Stop'

$taskName = 'JEVIX Supervision Agent'
& schtasks.exe /End /TN $taskName 2>$null
& schtasks.exe /Delete /TN $taskName /F
if ($LASTEXITCODE -ne 0) {
    throw "Impossible de supprimer la tâche planifiée (code $LASTEXITCODE)."
}

Write-Host 'Démarrage automatique désactivé.'
