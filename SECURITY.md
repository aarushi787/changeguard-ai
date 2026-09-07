# Security

## Implemented controls

- Server-side authenticated sessions: cryptographically random cookie, only its SHA-256 stored, eight-hour expiry; HttpOnly/SameSite=Strict; Secure in production.
- Scrypt password hashes with per-user random salt and constant-time hash comparison. New accounts require at least 12 characters.
- Server-side tenant checks on reads, writes, pages, references, jobs, tokens and reports. Resource enumeration across tenants returns 404.
- Strict Pydantic mutation models reject unknown fields and non-finite numbers. Roles and tenant IDs cannot be client-edited.
- Mutating requests require `X-ChangeGuard: 1`; browser Origin must match configured deployment origin. No permissive CORS configuration.
- Ten unsuccessful/successful login attempts per source address per minute in the single API process. Deploy shared gateway rate limits for multiple replicas. This in-memory guard is not a complete credential-abuse solution.
- Upload limits: 20 MB controlled file; 100 PDF pages; 25 megapixel image; Office archives maximum 2,000 entries/60 MB decompressed; no macro project; 10,000 canonical spreadsheet rows. Inventory maximum 2 MB/10,000 rows.
- Generated storage filenames, no public static document directory, attachment downloads, authenticated page rendering and `nosniff` headers.
- Download links use opaque random expiring capabilities, bound to issuing user, revision and tenant. They require authentication and expire in five minutes. They are **not** standalone public object-store signed URLs.
- Content security policy, no remote frontend fonts/scripts, strict framing restrictions, referrer policy, HSTS in production; Caddy TLS gateway.
- Database append-only audit triggers when migrated; ORM also prevents audit updates/deletes. Full original/edited evidence is kept for source corrections. App APIs provide no audit mutation operation.
- Approval invalidation after source, graph, inventory, action or document changes. Released source evidence is application-immutable. Engineering and quality reviewers must be different users.
- Source hashes checked before extraction, source display/download, report generation and approvals. Actual request bytes are bounded before multipart parsing; extraction runs in a 120-second subprocess. Optimistic record versions reject stale writes. Fingerprinted approvals and immutable release/extraction snapshots retain their decision context. Spreadsheet report strings are protected against formula injection.

## Role matrix

Administrator can perform all scoped operations; it cannot bypass two-person approval or release gates.

| Role | Scope |
|---|---|
| ENGINEER | Projects, uploads, source verification, dependencies, analysis, detection/document review, actions, engineering approval |
| QUALITY | Source verification, detection/document review, actions, independent quality approval |
| MANAGER | Projects, uploads, dependencies, actions, explicit release after both approvals |
| PLANNER | Inventory import, create actions, complete own actions, comment |
| PURCHASE | Create/complete own actions, comment |
| SUPPLIER_QUALITY | Create/complete own actions, comment |
| VIEWER | Authenticated read and report/export only |
| ADMIN | Team provisioning and all above, still constrained by release invariants |

An action can be completed only by its assigned user or manager/admin. Read access is tenant-wide in this MVP; project-level confidentiality subgroups are not implemented. Engineering roles such as design/process/manufacturing share ENGINEER. Plant head and engineering/quality manager can be provisioned MANAGER or the appropriate reviewer role. Dual-role reviewers currently need explicit admin scope or distinct accounts; fine-grained role composition is future work.

## Operational requirements before customer deployment

1. Use PostgreSQL migrations and separate migration-owner/runtime database roles. Revoke UPDATE/DELETE/TRUNCATE on audit_events and evidence_snapshots from runtime; the schema owner or database superuser can still bypass triggers. This is append-only application evidence, not tamper-proof storage against a privileged administrator.
2. Restrict database and private document volume access. Enable encrypted disks, encrypted backups and managed key controls. Application-level encryption at rest and object-store KMS are not implemented.
3. Use HTTPS with a valid certificate and exact APP_ORIGIN. Do not expose the API or database directly to the public network. Caddy is the only published service in the supplied stack.
4. Provision real accounts and remove demo data from production. Demo seeding refuses production unless explicitly overridden. Disable registration after onboarding. SSO, MFA, password recovery and account disablement workflows are not implemented.
5. Add gateway/shared rate limits, antivirus scanning and OS-level process sandbox/resource limits for untrusted documents. File validation is not malware detection.
6. Set document retention, incident response, tenant backup/restore and audit retention policy. There is no automatic purge; expired session/token records need an operational cleanup job.
7. Add PostgreSQL RLS or database-per-tenant if a stronger isolation boundary is required. The current boundary is application-enforced and tested locally, not database RLS.
8. Review dependency licenses and lock versions; run vulnerability scanning, load tests and independent security review. No compliance or certification is claimed.

## Local evaluation audit protection

Fresh setup uses `alembic upgrade head`, including snapshot and audit triggers. Existing reviewed 0001 databases upgrade with migration 0002; back up the database and private volume first. Do not stamp over an unknown or divergent schema. The prepared local evaluation database was backed up and migrated to 0002. Development `create_all` does not install triggers; always migrate a persistent deployment. Concurrent SQLite use remains evaluation-only.

## Reporting security issues

Report a reproducible scenario without customer drawing contents or credentials. Preserve the event ID, route, timestamp and generic error type. Do not publish private source files. Logs intentionally omit document contents, passwords, cookies and download-token query strings.
# Revision 3 security additions and limits

Universal changes have INTERNAL or COMMERCIAL classification. Commercial reads require a commercial role or an explicit administrator-issued grant for that specific change. Restricted lists, sources, graph, history and both synchronous/queued reports use the same access query. Revocation prevents future report downloads. People-sensitive structured field names are rejected; this is not a general DLP system.

Universal audit events never appear in the engineering tenant-wide audit feed. Per-change history and reports enforce classification/grants. Report jobs use a separate record kind so legacy job listing cannot expose their payloads. Download access is rechecked, not granted by possession of a URL.

Required evidence versions protect edits; independent approvals use evidence fingerprints; administrator stage bypass still cannot reuse the same human. Approved evidence is immutable through application routes. Named grants and feedback do not rewrite the signed technical evidence.

All processing works locally without external AI. Current private storage is filesystem based, and encryption in transit is supplied by the documented TLS gateway. Encryption at rest, KMS, malware scanning, RLS, SSO/MFA, restore drills and formal security assessment remain deployment responsibilities. The evaluated local server is bound only to 127.0.0.1.

## Shared workspace integration — September 2026

Unified workspace endpoints reuse authenticated tenant-scoped reads and the commercial access predicate. Drawing setup accepts only internal engineering changes, enforces engineering/manager/admin rights and expected versions, and rejects approved/terminal/completed-action conversions. Repeated setup is idempotent. A project lock plus the tenant mutation lock prevent duplicate linked comparisons on PostgreSQL. Alternate generic writes and report generation are blocked once drawing authority is selected. Prior source evidence and integration events remain auditable. Tests cover tenant, role, classification, stale-state, duplicate and release boundaries.
