# Setup

## Requirements

- Python 3.12, Node.js 22 or newer supported LTS and npm.
- PostgreSQL 16 for deployment; Docker Compose for the supplied stack.
- SQLite is an explicit local evaluation alternative, not the recommended deployment database.

Run commands from the repository root. No real customer drawings or secrets are needed to evaluate the demo.

## Fresh local installation (PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
npm.cmd ci
python scripts/make_samples.py
python -m alembic upgrade head
python -m backend.seed
npm.cmd run build
$env:APP_ORIGIN = 'http://127.0.0.1:8010'
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010 --no-access-log
```

Open `http://127.0.0.1:8010`. The build is served by FastAPI; UI and API share one origin. Cookies are HttpOnly and SameSite=Strict. Secure cookies are enabled in production mode, which therefore requires HTTPS.

## This prepared Windows workspace

During implementation, Windows sandbox permissions required three dependencies and their dependencies to be installed in `.vendor`. The globally available Python supplies the other packages. `scripts/start-local.ps1` includes `.vendor` in the Python path if present. If Windows blocks access to those package directories, run your own normal PowerShell session or use the clean virtual environment installation above.

```powershell
.\scripts\start-local.ps1
```

If port 8010 is occupied, choose another port and set `APP_ORIGIN` to the matching browser origin. Do not stop another application's server to free a port.

## Development mode

In terminal one, activate the environment and run FastAPI on 8010. In terminal two:

```powershell
npm.cmd run dev
```

Vite runs on `http://127.0.0.1:5173` and proxies `/api` to port 8010. Local mode permits these two loopback origins. Restart FastAPI after Python changes; rebuild frontend assets for the single-server build.

## Database and environment

Python reads exported environment variables, not `.env` automatically. Docker Compose reads `.env` for interpolation. Configuration:

| Variable | Default | Meaning |
|---|---|---|
| DATABASE_URL | sqlite:///./data/changeguard.db | SQLAlchemy database URL |
| STORAGE_PATH | data/documents | Private upload volume |
| ENVIRONMENT | unset/local | `production` enables Secure cookies, HSTS and disables automatic schema creation |
| APP_ORIGIN | http://127.0.0.1:5173 | Permitted frontend origin; exact production origin required |
| RUN_WORKER | 1 | Embedded evaluation worker; use 0 with a separate worker |
| ALLOW_REGISTRATION | 0 in production | Set to 1 only for controlled company onboarding |

On a fresh database, always use `python -m alembic upgrade head` before seeding. Local runtime auto-creation is a convenience; it does not install database audit triggers. The prepared demo database was initially auto-created, then its columns were checked against the baseline, immutable-audit triggers installed, and migration 0001 stamped using `scripts/secure_local_schema.py`. For new installations, migration-first avoids this extra step.

## Troubleshooting

- **401:** sign in again; sessions expire after eight hours.
- **403 Origin not allowed:** check the exact `APP_ORIGIN`, including scheme and port. Do not disable the origin check.
- **409 Release gates:** inspect the returned blocker list in Approvals. This is expected until human reviews are complete.
- **Stale analysis:** edits to source characteristics, dependency maps or inventory clear prior approvals. Re-run analysis, review regenerated actions/documents, then approve again.
- **QUEUED jobs:** run the embedded worker or `python -m backend.worker` with the same database and storage volume.
- **FAILED jobs:** inspect the job failure reason. Correct unsupported/malformed sources. Retry accepts failed jobs or RUNNING jobs older than ten minutes.
- **Blank image extraction:** expected without OCR. Use manual characteristic entry and check completeness against the source.
- **Spreadsheet rejection:** use the exact canonical header names from `samples/characteristics-A.csv`.
- **Unknown modules in script verification:** use `python -m scripts.verify_reports`, which retains the repository root on the module path.

## Upgrading the previous evaluation build

Stop this application's API and worker, back up the database and private document directory, run `python -m alembic upgrade head`, rebuild the interface and restart. For eligible fictional demo records run `python scripts/upgrade_demo_v2.py`. Do not use schema stamping in place of migrations. Run `python scripts/evaluate_engineering.py` to regenerate the documented synthetic challenge results.

The prepared workspace has been migrated to 0002 and contains a pre-upgrade SQLite backup in data/changeguard-before-v2.db. For fresh deployments use the migration-first steps above. Local OCR is optional; see AI_MODELS.md and DEPLOYMENT.md.
# Multi-domain upgrade

After installing the existing prerequisites, run `python -m alembic upgrade head`, `python -m scripts.seed_multidomain`, then rebuild with `npm run build`. Start the API with `scripts/start-local.ps1`. On Windows with the bundled local `.vendor` directory, set `PYTHONPATH=.vendor;.` for direct Python commands.

The default UI is the shared workspace. The drawing workbench is `/#engineering`. New demo credentials and scenario walkthroughs are in DEMO_GUIDE.md. Read KNOWN_LIMITATIONS.md before importing real company information.
