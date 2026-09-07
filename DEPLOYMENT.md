# Deployment and operations

## PostgreSQL + private worker + TLS gateway

The supplied stack has PostgreSQL 16, one migration job, API, separate extraction worker, and Caddy. API and worker share a private document volume. Only the gateway publishes ports. The image runs as a non-root user. Multi-stage frontend build serves static assets from the API origin.

```powershell
Copy-Item .env.example .env
# Edit .env: choose a URL-safe random database password and real hostname/origin.
docker compose build
docker compose up -d
docker compose logs -f api worker
```

Set SITE_ADDRESS to your real DNS hostname and APP_ORIGIN to `https://that-hostname`. DNS must point at the host for public TLS issuance. `localhost` uses Caddy's local CA, which must be installed/trusted through normal administrator procedures. Do not bypass browser certificate warnings. For the simple evaluation demo, use the local loopback setup instead of production Secure cookies over plain HTTP.

This Compose stack is **provided but was not executed here** because Docker/PostgreSQL are unavailable on this machine. Confirm volume ownership, image availability, TLS and migrations in your own staging environment before handling customer data.

## Onboarding

Temporarily set ALLOW_REGISTRATION=1, restart the API, create the company/admin and provision separate engineering/quality/manager users. Disable registration afterward. Do not load the fictional demo into a customer production database. `backend.seed` rejects ENVIRONMENT=production unless explicitly overridden with ALLOW_DEMO_SEED=1; use a separate evaluation environment instead.

## Migrations

Run the migrate service before API/worker. The initial migration creates all tables and append-only audit triggers. Runtime production mode does not auto-create schema. Destructive downgrade is explicitly disabled. Back up first, review migrations, apply through a dedicated schema owner and give the runtime account only required privileges. The supplied minimal Compose credentials use one database owner for simplicity; split them before a real customer deployment.

## Worker operation

Set RUN_WORKER=0 on API containers and run `python -m backend.worker` separately. Worker and API need identical DATABASE_URL and STORAGE_PATH. Queued records persist across restarts. A failed job shows a failure reason; a RUNNING job older than ten minutes can be retried by an authorized user. No automatic unbounded retry is performed.

Limit container CPU/memory and storage and introduce antivirus before accepting bulk/untrusted files. Extraction runs in a subprocess with a 120-second limit; local OCR calls have 25-second limits. UI report jobs capture immutable inputs but report generation itself has no hard timeout. Legacy synchronous exports remain for API compatibility. One worker is sufficient for the MVP; concurrent worker claims are implemented for PostgreSQL but need environment-specific stress testing.

## Health and observability

`GET /api/v1/health` checks database connectivity and returns the actual database/provider mode. API logs are JSON records with route, status, timing; jobs record duration, status, provider, zero model tokens and generic failure cause. Framework access logs should be configured at your gateway to avoid retaining sensitive query parameters; opaque source download tokens appear in URLs. The application structured logger records only URL paths. Keep request logging out of source contents.

Monitor failed jobs, queue age, storage free space, database connectivity and response errors. No external tracing backend, SIEM exporter, model cost billing or on-call alert pipeline is configured.

## Backup and restore

Back up PostgreSQL and the private document volume together with a consistent snapshot boundary; both are necessary for evidence provenance. Use encrypted storage and backups. Record backup time, schema revision and file hash manifest. Restore to an isolated environment, verify row counts/source hashes and run a release-gate smoke test before switching traffic. Never truncate audit tables to resolve a deployment failure.

## Private cloud / on-premise

No external model or font network access is required at runtime. Package/image downloads are needed at build time unless mirrored internally. The architecture can run within a private network using an internal TLS gateway and controlled database/document volumes. KMS, S3-compatible storage, SSO, MFA, RLS, retention scheduling and compliance attestations remain deployment engineering work.

## Revision 2 upgrade and OCR

Back up DB and source volume. Run `python -m alembic upgrade head` before starting upgraded API/workers. Existing fictional demo only: `python scripts/upgrade_demo_v2.py` adds annotation geometry/mappings and reanalyzes under CG-2.0 while retaining legacy evidence snapshots. It skips already upgraded or released/approved demo projects and never targets customer tenants. A prepared local backup exists at data/changeguard-before-v2.db.

The image copies `rules/` and installs local Tesseract. Windows/local environments can install a supported Tesseract package and set TESSERACT_CMD to its executable path. Check /api/v1/health before claiming OCR is configured. An available executable is not evidence of validated engineering OCR accuracy. The current Windows run reports not_configured.

Cloud, private-cloud and on-premise use the same application. No runtime outbound model calls or remote fonts are required. Secrets belong in deployment secret storage, not source control. The image and PostgreSQL/TLS deployment must still be exercised in staging.
# Revision 3 deployment notes

## Vercel frontend routing

### Persistent backend on Render

`render.yaml` defines a single Docker service in Singapore with 1 GB of persistent storage. Review and approve Render billing before creating the service. Startup uses `python -m scripts.start_cloud`: migrations must succeed before the server listens on Render's PORT. The embedded database worker shares this service's disk; keep one instance. Render's disk prevents zero-downtime deployments, so brief deployment downtime is expected. This is a pilot sizing choice, not a capacity guarantee.

Set DATABASE_URL through Render's secret environment settings. APP_ORIGIN is the Vercel frontend URL, ENVIRONMENT=production, RUN_WORKER=1, STORAGE_PATH=/app/data/documents and ALLOW_REGISTRATION=0. Existing demo accounts can sign in; company registration remains intentionally closed unless explicitly enabled. For this existing fictional Supabase demo, set RESTORE_BUNDLED_DEMO=1 once: it restores only bundled CSV files matching the saved source hash and never overwrites differing evidence. It does not migrate real customer documents. Remove this flag after the initial successful deployment.

Before enabling the cloud worker against this database, stop the local Supabase worker: independent local and Render disks cannot serve each other's jobs. Transfer any non-demo documents through an authenticated administrative channel and verify hashes before switching traffic. Keep the old SQLite installation separate.

Once Render assigns the actual HTTPS hostname, configure a Vercel rewrite from `/api/:path*` to `https://<verified-backend-host>/api/:path*`. Do not guess the hostname or publish a placeholder rewrite. Redeploy Vercel, then verify health, sign-in, source download and report completion through its public domain.

Deploying the Vite `dist` directory publishes only the frontend. Supabase provides PostgreSQL; it does not host this FastAPI application. A frontend-only deployment returns 404 for `/api/v1/auth/me`, `/api/v1/auth/login` and `/api/v1/auth/register`.

Run the provided Docker image as a persistent backend with its database secret, a private document volume, migrations and a worker. Route all `/api/:path*` requests from the frontend origin to that backend, preserving the complete `/api/` path. Configure APP_ORIGIN to the exact public frontend origin (for this deployment, `https://changeguard-ai.vercel.app`). Preserve Set-Cookie response headers. Do not direct API requests to the Supabase project URL, and never put the database secret in a VITE variable. A publicly hosted frontend cannot reach the developer machine's loopback address.

Verify `/api/v1/health` returns JSON with status `ok` through the public frontend domain, then `/api/v1/auth/me` returns 401 when signed out. A 404 or HTML response indicates missing API routing. Only after those checks should login, registration policy, file downloads and queued processing be verified. The frontend now distinguishes an unavailable API from a normal signed-out session.

Apply Alembic migration 0003 before starting the updated API/worker. Docker now includes `domain_packs/`. Both API and worker must deploy the same code, pack files, database and private source volume. The existing Compose PostgreSQL/TLS topology remains the production deployment starting point.

For a **separate demonstration deployment**, run `python -m scripts.seed_multidomain` after migrations. Never run demo seeding automatically in a production startup command. Production seeding remains blocked unless `ALLOW_DEMO_SEED=1` is explicitly set. The seed creates a new PRAGATI tenant and preserves Northstar records.

Universal structured parsing is bounded and performed off the async event loop. Universal reports use durable database jobs; RUN_WORKER=0 on the API and the separate worker service are recommended for deployment. The local evaluation server embeds a worker. Queues do not yet provide fair scheduling, cancellation, resource hard timeouts or abandoned-job recovery for universal reports.

Cloud/private cloud/on-premise all use the same AI-off core. No external provider is needed. Infrastructure credentials, backup encryption, storage access, independent security assessment and restore drills must be supplied before a real confidential-data pilot. PostgreSQL and Docker execution were not available on this Windows host; configuration and SQLite tests are not a substitute for staging verification.
