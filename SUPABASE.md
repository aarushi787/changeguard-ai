# Supabase database connection

Supabase hosts PostgreSQL; FastAPI retains authentication, tenant authorization, jobs and approvals. No Supabase service key or database credential belongs in frontend code. Document bytes remain in private application storage; changing database does not copy existing SQLite records or files.

## Connect locally

The backend automatically loads the repository-root `.env` for local use. Store `DATABASE_URL`, `APP_ORIGIN=http://127.0.0.1:8011`, `STORAGE_PATH=data/supabase-documents` and local worker settings there. Explicit environment variables take precedence, and tests do not load this file. The local private `.env` is excluded from Git. Run `./scripts/start-supabase.ps1` to use it, or `python -m scripts.verify_supabase` to verify connectivity. A local `.env` does not deploy the backend to Vercel; cloud services need their own server-side secret settings.

1. Open your Supabase **project**, then **Connect**. Copy the PostgreSQL direct URL (IPv6), or session pooler URL on port 5432 for IPv4. Transaction pooling on 6543 is intentionally rejected by this configuration.
2. From the project directory, set `$env:PYTHONPATH='.vendor;.'` if using bundled local dependencies. Run `python -m scripts.configure_supabase` in an interactive terminal. Paste the URL with the database password at the hidden prompt; URL-encode special password characters. It verifies connectivity without printing credentials and saves to Git-ignored `data/supabase-database-url.txt`. Restrict Windows file access to your account; chmod alone does not configure Windows ACLs. For hosted deployments use a secret manager instead.
3. Run `./scripts/start-supabase.ps1`. This migrates the database and starts at http://127.0.0.1:8011, leaving the SQLite demo on 8010 intact. It does not silently copy or seed data.
4. For a dedicated fictional demo only, export `$env:DATABASE_URL_FILE=(Resolve-Path 'data/supabase-database-url.txt').Path` and `$env:STORAGE_PATH='data/supabase-documents'`, then run `python -m scripts.seed_multidomain`. Demo login is `admin@pragati.changeguard.demo`, password `ChangeGuard!2026`. Do not seed shared production databases.
5. Run `python -m scripts.verify_supabase` with the same database environment to check the actual session schema, client TLS, migration and API-role restrictions without displaying credentials.

## Storage boundary and deployment

All Supabase connections require TLS and use the private `changeguard` schema. Online Alembic migrations create this schema and revoke schema access from PUBLIC, anon and authenticated. Keep it out of Supabase Data API exposed schemas. Supabase Auth is not used. Tenant permissions are enforced by FastAPI, not PostgreSQL tenant RLS. Use a dedicated project and restrict backend database credentials. The migration user must be able to create schemas/tables/functions. A separately provisioned runtime role should receive only required application permissions before production rollout.

API, worker and migration processes must use the same DATABASE_URL or DATABASE_URL_FILE and shared document storage. The existing compose.yaml deploys its own PostgreSQL; it is not a Supabase deployment. Configure a separate hosted API/worker with Supabase secrets and run migrations before startup. Use verify-full with a trusted server certificate for production identity verification. Back up database and document storage together. Offline migration SQL generation is not the Supabase schema bootstrap path.

Connection setup alone does not migrate local records/accounts. The private schema is selected using an explicit SQL session setting on every new connection, because the hosted session pooler ignored startup options during live verification. Client TLS is checked with libpq; pg_stat_ssl behind a pooler describes the separate pooler-to-database link.

## Verified deployment — 7 September 2026

The dedicated ChangeGuard Supabase project was connected and migrated through revision 0003. Verification confirmed the `changeguard` schema, encrypted client connection, and denied schema access for both anonymous and authenticated Data API roles. Six fictional PRAGATI accounts and three unapproved demonstration changes were seeded. Every account passed live login and change-list checks. The browser dashboard displayed all three scenarios. Database/API regression suite: 22 passed. The local Supabase-backed app runs on port 8011 with separate document storage; the existing SQLite installation is preserved.

Windows credential-file ACLs were restricted to the account running setup and SYSTEM. No database password is committed. This is a local backend using a hosted database, not a publicly hosted application. Existing SQLite history was not copied.

References: [Supabase database connections](https://supabase.com/docs/guides/database/connecting-to-postgres), [Data API security](https://supabase.com/docs/guides/api/securing-your-api).
