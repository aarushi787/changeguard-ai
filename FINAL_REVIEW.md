# ChangeGuard AI — expert audit and implementation review

Prepared for MCCIA AI Applied Studio, 6 September 2026. The platform is a materially improved working evaluation MVP. It is not certified manufacturing software and is not approved for unattended customer production use.

## 1. Current-system audit

Read the repository's frontend, backend, schemas, migrations, rules, provider contracts, security, worker, reports, tests, samples, dependencies, deployment configuration and all operating documentation before changing code. Inspected the running interface and ran the baseline: 37 tests passed. There is no Git repository/history in this workspace. The baseline system map and 20 prioritized findings are in AUDIT.md.

## 2. Problems discovered

P0 findings included numeric equality hiding changed callouts/critical flags, exact-ID-only relocation handling, retry overwrites, no sealed approval fingerprint, trusting Content-Length, narrow extraction, and no source-linked verification workbench. P1 included unstable balloon numbers, hidden score increments, untyped graph edges, misleading zero exposure, weak reports, missing release snapshots, unverified infrastructure and absent measured evaluation. P2/P3 included workbook onboarding, reference retrieval limitations and unavailable CAD/advanced AI adapters.

## 3. Improvements implemented

Staged local extraction; asymmetric/angle/quantity/thread/finish parsing; optional OCR; repeated-ID retention; immutable original extraction; original/corrected values; source-linked verification; reject/flag/merge/split/manual addition; persistent balloon numbering/positioning and leader lines; structured comparisons with qualifier/CTQ detection and 80% band calculation; configurable, versioned rule evidence and visible score increments; typed graph persistence with actual relationship lists; process/Control Plan/PFMEA import templates and preview/commit; stronger source/hash/concurrency/release protections; queued PDF/Excel/JSON exports with source excerpts and full source/project audit context; synthetic challenge evaluation; refreshed documentation.

## 4. Architecture before vs after

Before: React shell → monolithic FastAPI → JSON aggregates → single deterministic parser/comparator/risk function → generic graph → two-person review → synchronous report.

After: React shell plus engineering workbench → tenant/RBAC/body-limit boundary → versioned aggregates, typed edges and immutable evidence → bounded staged extraction subprocess → semantic comparator → versioned rule engine + graph evidence → attributed source/action/document review → fingerprinted two-person approval → manager release snapshot → queued evidence reports. PostgreSQL remains the deployment target; Neo4j and external LLMs are unnecessary for this MVP.

## 5. Database changes

Alembic 0002 adds records.version, knowledge_edges and evidence_snapshots, indexes, relationship uniqueness and append-only snapshot triggers. The local database was backed up before migration. Unreleased fictional demo records were upgraded through an idempotent audited script; original evidence/analysis snapshots were retained. Released records are excluded from that script.

## 6. AI pipeline

PDF text/layout and optional local OCR feed deterministic engineering grammar, provenance reconciliation and completeness review. CSV/XLSX canonical imports retain strict required limits. DOCX retains logical text positions. No LLM math, automatic cloud transfer or invented GD&T interpretation. Confidence labels are heuristic and not calibrated probabilities. Scans require installed OCR or manual entry; the local executable is absent here.

## 7. Rules architecture

CG-2.0 JSON rules identify tightening, material/GD&T changes, critical/safety relevance, stock/supplier exposure and uncertainty. Recommendations expose WHY, SOURCE, CONFIDENCE and ENGINE with rule IDs. Risk increments and cap are visible. Capability remains UNKNOWN until humans check evidence. Both old and new critical/safety designations count.

## 8. Security improvements

Actual-byte request limits, bounded extraction subprocesses, source rehashing, optimistic conflict rejection, protected reviewed/released retries, source-preserving corrections, approval fingerprints and immutable release snapshots complement existing cookies, RBAC, tenant checks, CSRF/origin checks, private storage and audit triggers. No independent penetration test, MFA/SSO, antivirus, RLS, encrypted storage adapter or restore drill is claimed. Runtime/schema-owner credentials must be separated for a customer deployment.

## 9–10. Tests performed and results

The final regression suite passed **63 tests in 69.74 seconds**. The final TypeScript/Vite production build passed. Results and reproduction commands are recorded in TESTING.md. Coverage includes parser fixtures, comparison arithmetic and false positives, qualifier/CTQ changes, ambiguous relocation, low confidence, actual chunked limits, source tampering, tenant/role checks, merge/split preservation, annotation mapping, queued exports, workbook preview/commit, optimistic concurrency, immutable migration triggers, and complete independent-review/release workflow. TypeScript/Vite build passed. Browser inspection confirmed desktop source highlighting, comparison metrics, queued report completion and no browser console errors. PDFs were rendered and inspected; C27 exports as balloon 27.

Synthetic evaluation: 6 exact numeric predictions from 10 expected characteristics; all 6 predictions were correct in this small authored set, with 4 misses and no false positives. Six semantic comparison scenarios passed. The misses are retained and named. This does not establish production accuracy. Independent impact-rule precision, human correction rate and representative real-drawing performance remain unmeasured.

## 11. Known limitations

- No reliable general geometric understanding, automatic visual registration, limit-only parsing, complete GD&T interpretation or native CAD adapters.
- Optional OCR is implemented but not exercised with a real OCR executable on this host. Rotated scans are not automatically deskewed/orientation-selected.
- Matching is conservative; ambiguous IDs require reconciliation. Not all drawing requirements are extracted. Human completeness is mandatory.
- Process/quality templates import relationships, not arbitrary legacy workbook semantics or controlled document content edits.
- PostgreSQL, Docker, TLS issuance, multi-worker stress and backup recovery were not executable here; supplied deployment configuration requires staging validation.
- Report jobs are asynchronous but lack hard execution timeouts and retention cleanup. Large histories and bulk imports need load testing.
- Reports include first-page source excerpts, not full visual diff markup for every page. All pages remain available in the workbench.
- Lexical references only; no embeddings/generative RAG, automatic standard interpretation or universal legacy source reopening.
- Fixed two-reviewer minimum; no workflow designer, approval delegation, PLM/ERP/MES/QMS synchronization or automated customer submission.
- Inventory is an imported snapshot. Open purchase orders, supplier stock and missing inventory cannot be inferred. Scores are priorities, not failure probabilities.

## 12. Demo instructions

Start the local server per SETUP.md and open http://127.0.0.1:8010. Sign in with engineer@changeguard.demo / ChangeGuard!2026. Open Bearing seat tolerance refinement. Drawing Comparison shows C27: ±0.10 → ±0.02, band 0.20 → 0.04 mm, 80% reduction, 5× tightening. Characteristics opens the source workbench; Impact Map explains OP30, CNC-04, T08, CMM, CP-021/PF-021 and 147 WIP plus 82 finished fictional units. Review sources and completeness, verify dependencies, reanalyze, disposition changes, complete documents/actions, then use different engineering/quality accounts and the manager for release. Never treat the demo as manufacturing evidence. Export report and inspect Audit Trail. DEMO.md covers exact accounts and safe steps.

## 13. Deployment instructions

Local: install requirements, npm ci, alembic upgrade head, seed, npm run build and start-local.ps1. Existing evaluation databases: back up both DB and source volume, migrate, then optionally run scripts/upgrade_demo_v2.py for fictional records. Production candidate: configure PostgreSQL, encrypted private volumes, least-privilege runtime role, valid TLS/APP_ORIGIN and separate worker; build the supplied Compose image, run migrations and validate in staging. Dockerfile includes local Tesseract and versioned rules. Do not expose local evaluation mode to customer traffic. DEPLOYMENT.md and SECURITY.md enumerate remaining operational requirements.

## 14. Next ten highest-value improvements

1. Execute PostgreSQL/Compose staging, concurrent approval/worker stress tests and consistent backup/restore drills.
2. Establish a representative, permissioned drawing corpus and independent engineer ground truth with precision/recall and correction-time measurements.
3. Validate local OCR, deskew/orientation, text/line separation and scanned-drawing confidence against that corpus.
4. Implement deterministic limit dimensions, richer callouts and qualified GD&T frame parsing with standards-specific validation.
5. Add spatial feature matching with ambiguity review and a manual correspondence editor across revisions.
6. Separate database owner/runtime privileges; add SSO/MFA, account disablement, malware scanning and audit external retention.
7. Add process/inspection capability evidence records and richer fixture/datum/CMM dependencies without inferring unsupported capability.
8. Add inventory import coverage declarations, purchase/production order adapters and explicit snapshot age/coverage warnings.
9. Add bounded report workers, pagination, resource/queue limits, retries, retention and load-test budgets.
10. Pilot with MSME engineers to measure time saved, improve keyboard/source navigation and introduce provenance-backed reference retrieval only where it resolves review work.
