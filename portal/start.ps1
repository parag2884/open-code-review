$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not $root) { $root = (Get-Location).Path }
if ((Split-Path -Leaf $PSScriptRoot) -eq "portal") {
    $root = Split-Path -Parent $PSScriptRoot
}

Write-Host "Installing Python dependencies..."
python -m pip install -r (Join-Path $root "portal\backend\requirements.txt")

Write-Host "Installing frontend dependencies..."
Push-Location (Join-Path $root "portal\frontend")
npm install
Pop-Location

Write-Host "API:  http://127.0.0.1:8080"
Write-Host "UI:   http://127.0.0.1:5173"
Write-Host "Start API and UI in two terminals if this script is used only for install."
Write-Host "  python -m uvicorn app.main:app --app-dir portal\backend --host 127.0.0.1 --port 8080"
Write-Host "  npm run dev --prefix portal\frontend"
