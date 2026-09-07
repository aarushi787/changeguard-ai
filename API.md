# API v1

Base: `/api/v1`. Interactive OpenAPI schema: `/docs`; raw schema: `/openapi.json`. The default strict CSP can prevent third-party Swagger UI assets from loading; use the raw schema or an internally hosted API client rather than weakening production CSP.

Authenticated routes use the `cg_session` HttpOnly cookie. All mutations, including login, need `X-ChangeGuard: 1`. Browser mutations must originate at APP_ORIGIN. Errors use HTTP 401/403/404/409/413/422/429 as appropriate; workflow blockers appear under `detail.blockers` in a 409.

## Identity

| Method | Path | Purpose |
|---|---|---|
| POST | /auth/register | Create company + admin; disabled by default in production |
| POST | /auth/login | Authenticate and issue cookie |
| POST | /auth/logout | Revoke session |
| GET | /auth/me | Identity, organization, role, pack |
| GET / POST | /users | List team / administrator provisions a user |

Example login body:

```json
{"email":"engineer@changeguard.demo","password":"ChangeGuard!2026"}
```

## Projects and source revisions

| Method | Path | Purpose |
|---|---|---|
| GET / POST | /projects | List/create projects |
| GET | /projects/{id} | Project and directed dependency graph |
| PUT | /projects/{id}/graph | Replace/verify nodes and edges with rationale; invalidates current analysis |
| GET | /projects/{id}/revisions | Revision characteristics and extraction status |
| POST | /projects/{id}/revisions?revision=A | Multipart `file`; persist source + enqueue job; 202 |
| PUT | /revisions/{id}/characteristics/{cid} | Correct/verify characteristic, or manually add missing stable ID |
| POST | /revisions/{id}/verify-completeness | Human source completeness statement after every characteristic is verified |
| GET | /revisions/{id}/pages/{page} | Authenticated PDF/image page rendering |
| GET | /revisions/{id}/download-token | Issue expiring user-bound download capability |
| GET | /revisions/{id}/file?token=... | Authenticated source download |
| GET | /revisions/{id}/balloons?format=pdf | Ballooned source PDF; requires boxes |
| GET | /revisions/{id}/balloons?format=xlsx | Inspection characteristic list |
| POST | /projects/{id}/inventory | Multipart canonical CSV; replace snapshot and invalidate analysis |

Characteristic corrections require reason, characteristic_id, label, type, nominal/tolerance values (or null for text), unit, raw, source_page, critical and safety flags. Server sets verification identity/time. Released revisions reject edits.

## Change analysis and review

| Method | Path | Purpose |
|---|---|---|
| GET / POST | /change-sets | Register/create semantic comparison |
| GET | /change-sets/{id} | Full analyzed aggregate |
| POST | /change-sets/{id}/reanalyze | Recompute from current evidence; clear approvals, document/detection decisions and regenerate automatic actions |
| POST | /change-sets/{id}/changes/{cid}/review | ACCEPTED / REJECTED / FLAGGED plus reason |
| POST | /change-sets/{id}/actions | Assign title, owner_id, due_date, reason |
| PATCH | /change-sets/{id}/actions/{aid} | OPEN / COMPLETE plus reason |
| PATCH | /change-sets/{id}/documents/{did} | PENDING / REVIEWED / NOT_APPLICABLE, owner, due_date, reason |
| POST | /change-sets/{id}/comments | Append engineering discussion with `reason` as text |
| GET | /change-sets/{id}/release-gates | Blocker list and required approvals |
| POST | /change-sets/{id}/transition | Reasoned human workflow action |
| GET | /change-sets/{id}/report?format=pdf&kind=impact | PDF or XLSX; kind impact/comparison/documents/actions/approvals |

Comparison body:

```json
{"project_id":"...","old_revision_id":"...","new_revision_id":"...","title":"Bearing seat tolerance refinement"}
```

Transition actions: START_REVIEW, REQUEST_ACTION, ENGINEERING_APPROVE, QUALITY_APPROVE, REJECT, RELEASE. All require a rationale of 5–1,000 characters. REJECT returns the change set to ACTION_REQUIRED; REJECTED detection is a separate false-positive decision and does not reject the whole engineering change. Reanalysis retains manually created actions, but generated actions are regenerated OPEN and prior document/detection reviews must be repeated.

## Knowledge, operations and audit

| Method | Path | Purpose |
|---|---|---|
| POST | /knowledge | Multipart reference upload and private text indexing |
| GET | /knowledge/search?q=... | Lexical excerpts with source location/hash |
| GET | /jobs | Tenant job status, duration, provider, failures |
| POST | /jobs/{id}/retry | Failed/abandoned extraction retry |
| GET | /audit?entity=...&offset=0&limit=1000 | Paged scoped audit records; optional entity filter; maximum 1,000 per page |
| GET | /capabilities | Honest processing support/limitations |
| GET | /health | Database connectivity and provider status; no credentials |

Resource IDs from another tenant return 404. Cross-tenant ownership checks also apply to referenced projects, revisions, action owners and source download tokens. No endpoint automatically approves/releases revisions or scraps/blocks inventory.

The MVP returns aggregate lists for most resources. Audit supports offset/limit pagination; the UI and reports fetch subsequent pages so the complete retained history remains accessible. Cursor-based consistent snapshot exports and large-history virtualization are future scale improvements. External integration clients should preserve optimistic revision context and not assume this interface implements ERP transactions.

## Revision 2 endpoints

All routes remain under /api/v1 and require authentication and tenant ownership. Mutations require X-ChangeGuard: 1 and an allowed Origin. Version conflicts return 409.

| Method / path | Purpose |
|---|---|
| POST revisions/{id}/characteristics/{cid}/decision | VERIFIED, REJECTED or REVIEW_REQUIRED, with reason; unresolved numeric units cannot be verified |
| PATCH revisions/{id}/characteristics/{cid}/annotation | Unique balloon_number, optional x/y page coordinates and reason |
| POST revisions/{id}/reconcile | source_ids, replacement CharacteristicInput objects and reason; retains superseded originals and new review-required evidence |
| GET change-sets/{id}/matching | Full semantic matching including unchanged/moved/visual-only results; not an approval |
| GET templates/{process,control-plan,pfmea} | Canonical relationship workbook with fictional example |
| POST projects/{id}/dependency-import?commit=false | Multipart CSV/XLSX validation and preview; commit=true saves mappings and invalidates completeness/approvals |
| POST change-sets/{id}/report-jobs | format pdf/xlsx/json and report kind; returns 202 with durable job ID |
| GET jobs/{id} | Safe status/timing; report payload and private keys omitted |
| GET jobs/{id}/report-download | Authenticated completed artifact; checks hash |
| GET change-sets/{id}/report?format=json | Legacy synchronous JSON export, alongside PDF/XLSX |

Characteristic PUT additionally accepts quantity and a four-coordinate bbox. Coordinates must lie on a known source page. Reconciliation replacements require new unique IDs; verification is a separate step. Typed graph edges support a relation field. Workbook import retains filename/hash/row provenance. Full API contracts are exposed at /docs and /openapi.json on the local server.
# Revision 3 universal endpoints

All routes below use `/api/v1`, the same authenticated session cookie and `X-ChangeGuard: 1` mutation header. Mutations carry `expected_version` and a meaningful `reason` unless creating a new change or queueing a report. OpenAPI is available at `/docs` and `/openapi.json`.

| Route | Purpose |
|---|---|
| GET /domain-packs | Available and planned packs; AI-off capability |
| GET/POST /changes | Tenant/access-filtered paginated list; create controlled change |
| GET /changes/{id} | Full authorized evidence and gates |
| PUT /changes/{id}/sources/{old,new} | Manual canonical rows |
| POST /changes/{id}/sources/{side}/upload | CSV/XLSX/JSON multipart upload |
| PATCH /changes/{id}/sources/{side}/correction | Preserve original, correct a field |
| POST /changes/{id}/sources/{side}/verify | Human completeness verification |
| GET /changes/{id}/sources/{side}/download | Private, integrity-checked source |
| POST /changes/{id}/compare | Deterministic analysis and action generation |
| POST /changes/{id}/deltas/{delta}/review | Confirm, ignore, informational or flag |
| PUT /changes/{id}/graph?preview=true | Validate graph without writing; omit preview to commit |
| POST /changes/{id}/graph/verify | Explicit scope/freshness review |
| GET /changes/{id}/impact | Bounded paths, depth/limit controls |
| POST /changes/{id}/actions | Assign a review task |
| PATCH /changes/{id}/actions/{action} | Owner/manager update with completion evidence |
| POST /changes/{id}/approve | Independent approval/effectivity/disposition command |
| GET /changes/{id}/audit | Access-filtered paginated immutable history |
| POST /changes/{id}/access | Admin named reviewer grant/revocation |
| POST /changes/{id}/feedback | Record outcome pending admin review |
| GET /imports/templates/{domain} | CSV/Excel source or relationships template |
| POST /imports/{id}/dependencies | Excel/CSV relationship preview; commit=true to save |
| GET/PUT /domain-settings | Admin rule point overrides; invalidate open analyses |
| POST /changes/{id}/report-jobs | Freeze and queue PDF/Excel/JSON evidence report |
| GET /reports/{job} | Access-checked generation status |
| GET /reports/{job}/download | Access-checked, hash-verified report |
| GET /changes/{id}/report | Synchronous small-integration export |

404 intentionally hides cross-tenant and unauthorized commercial records. 409 indicates stale version, missing gates, source corruption or invalid state transition. 422 identifies invalid input. Named grants never bypass tenant scope or approval-role checks. Integration events are retained locally as NOT_DISPATCHED; no outbound connector endpoint is claimed.

## Shared workspace integration — September 2026

`GET /api/v1/workspace/changes?offset=0&limit=200` returns the shared register. `GET /api/v1/workspace/changes/{id}` returns the active workflow and evidence-routing references. `POST /api/v1/workspace/changes/{id}/drawing-workspace` takes `expected_version`, `part`, optional `customer`, and `reason`. Requires an internal engineering change and engineering/manager/admin authority. Conversion is idempotent; reviewed/approved evidence cannot switch authority. Existing drawing upload/comparison/review/report endpoints remain authoritative for DRAWING records. Generic write/report endpoints return 409 after linking. Old read endpoints remain for historical API compatibility; integrations should use the workspace projection for current status.
