$ErrorActionPreference = 'Stop'

if ($env:OS -ne 'Windows_NT') {
    throw 'Build this executable on Windows to produce a Windows binary.'
}

$projectDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$dependenciesDir = Join-Path $projectDir 'build-deps'
$previousPythonPath = $env:PYTHONPATH
Push-Location $projectDir
try {
    python -m pip install --target $dependenciesDir -r requirements-agent-build.txt
    if ($LASTEXITCODE -ne 0) { throw 'Installing build dependencies failed.' }

    if ($previousPythonPath) {
        $env:PYTHONPATH = "$dependenciesDir$([IO.Path]::PathSeparator)$previousPythonPath"
    }
    else {
        $env:PYTHONPATH = $dependenciesDir
    }

    python -m PyInstaller --noconfirm --clean --onefile --console `
        --name JEVIX-Agent agent.py
    if ($LASTEXITCODE -ne 0) { throw 'PyInstaller failed to build the agent.' }

    Copy-Item -LiteralPath 'agent_config.example.json' `
        -Destination 'dist\agent_config.json' -Force
    Write-Host 'Build complete: dist\JEVIX-Agent.exe'
    Write-Host 'Edit dist\agent_config.json and set the server IP before running.'
}
finally {
    $env:PYTHONPATH = $previousPythonPath
    Pop-Location
}
