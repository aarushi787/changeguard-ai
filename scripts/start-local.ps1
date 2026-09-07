$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
if (Test-Path -LiteralPath '.vendor') { $env:PYTHONPATH = (Resolve-Path -LiteralPath '.vendor').Path }
$env:APP_ORIGIN = 'http://127.0.0.1:8010'
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010 --no-access-log
