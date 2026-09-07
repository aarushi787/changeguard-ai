param([int]$Port = 8011)
$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $PSScriptRoot)
if (Test-Path -LiteralPath '.vendor') { $env:PYTHONPATH = (Resolve-Path -LiteralPath '.vendor').Path }
if (-not (Test-Path -LiteralPath 'data/supabase-database-url.txt')) { throw 'Run python -m scripts.configure_supabase interactively first.' }
if ($env:DATABASE_URL) { throw 'Clear DATABASE_URL before starting with the Supabase credential file.' }
$env:DATABASE_URL_FILE = (Resolve-Path -LiteralPath 'data/supabase-database-url.txt').Path
if (-not $env:STORAGE_PATH) { $env:STORAGE_PATH = 'data/supabase-documents' }
$env:APP_ORIGIN = "http://127.0.0.1:$Port"
python -m alembic upgrade head
if ($LASTEXITCODE -ne 0) { throw 'Database migration failed. Server was not started.' }
python -m uvicorn backend.main:app --host 127.0.0.1 --port $Port --no-access-log
