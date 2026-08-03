# RiskAtlas local dev: postgres + redis (docker) + API (uvicorn) + web (next)
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[start] .env created from .env.example - edit LLM/data-source keys if needed."
}

Write-Host "[start] starting postgres + redis ..."
docker compose up -d --wait postgres redis
if ($LASTEXITCODE -ne 0) { throw "docker compose failed - is Docker Desktop running?" }

$venvPython = Join-Path $root "apps/api/.venv/Scripts/python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[start] creating API venv and installing deps ..."
    py -3.12 -m venv "apps/api/.venv"
    if ($LASTEXITCODE -ne 0) { throw "failed to create venv (need Python 3.12)" }
    & $venvPython -m pip install -e "apps/api[dev]"
    if ($LASTEXITCODE -ne 0) { throw "pip install failed" }
}

Write-Host "[start] starting API (uvicorn) on :8000 ..."
$apiProc = Start-Process -FilePath $venvPython -ArgumentList "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload" `
    -WorkingDirectory (Join-Path $root "apps/api") -NoNewWindow -PassThru

try {
    Write-Host "[start] starting web (next dev) on :3000 ..."
    pnpm --filter @riskatlas/web dev
} finally {
    if ($apiProc -and -not $apiProc.HasExited) { Stop-Process -Id $apiProc.Id -Force }
}
