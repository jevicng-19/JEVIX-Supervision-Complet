$ErrorActionPreference = 'Stop'

$taskName = 'JEVIX Supervision Agent'
$exePath = Join-Path $PSScriptRoot 'JEVIX-Agent.exe'

if (-not (Test-Path -LiteralPath $exePath)) {
    throw "JEVIX-Agent.exe est introuvable dans $PSScriptRoot."
}

if (-not (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'agent_config.json'))) {
    throw "agent_config.json est introuvable dans $PSScriptRoot."
}

$taskAction = '"' + $exePath + '"'
& schtasks.exe /Create /SC ONLOGON /TN $taskName /TR $taskAction /F
if ($LASTEXITCODE -ne 0) {
    throw "Impossible de créer la tâche planifiée (code $LASTEXITCODE)."
}

& schtasks.exe /Run /TN $taskName
if ($LASTEXITCODE -ne 0) {
    throw "La tâche a été créée, mais son démarrage immédiat a échoué (code $LASTEXITCODE)."
}

Write-Host 'Démarrage automatique activé. L’agent est lancé maintenant et démarrera à chaque ouverture de session Windows.'
