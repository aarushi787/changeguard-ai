# Testing and verification

## Automated commands

From the root in the configured Python environment:

```powershell
python -m pytest -q
npm.cmd run build
python -m scripts.verify_reports
```

For the prepared workspace's project-local dependencies:

```powershell
$env:PYTHONPATH = '.vendor;.'
python -m pytest -q
python -m scripts.verify_reports
```

Tests create an isolated SQLite database and storage directory under `tmp/`. They never modify the demonstration workspace database. Runtime environment variables are set before backend import. Worker execution is deterministic in tests; `process_one()` advances queued extraction jobs.

## Covered behavior

- Golden CSV and authored PDF extraction, source pages/boxes/rows and material metadata.
- 5× tolerance tightening, relaxation, shifted intervals, unknown unit changes, add/remove.
- No false positive for equal parsed values when raw notation/location changes.
- Low-confidence GD&T is never interpreted; unsupported OCR returns no invented dimensions.
- Cyclic directed graph traversal; disconnected entities are excluded.
- Explicit mock provider selection; missing cloud/local provider fails closed.
- Invalid PDF/image/Office/CAD input, macro Office archives, upload size, duplicate revisions, duplicate characteristic IDs, NaN.
- Company registration, authentication, CSRF header and foreign-origin rejection.
- API tenant isolation for project, revision, report, page, token and workflow routes.
- Read-only role cannot mutate or provision an administrator.
- Full fixture workflow: upload -> process -> compare -> verify -> map -> reanalyze -> document/action review -> independent engineering/quality -> manager release.
- Release gating, forbidden sequence, same-user dual approval rejected, quality role cannot release.
- Source edit invalidates prior approvals; released source and change analysis reject mutation.
- Authenticated download capability scope and invalidation on logout.
- Processing failure recorded; inventory import invalidates old analysis.
- Private reference retrieval retains hashes and locations.
- PDF/XLSX report generation, workbook formula-injection prevention.
- ORM audit immutability and fresh Alembic SQLite migration database delete protection.

## Revision 2 verification

Baseline: 37 tests passed before modifications. Expanded runs passed 55, 60 and 62 tests as capabilities were added. **Final regression: 63 tests passed in 69.74 seconds.** Final TypeScript/Vite production build passed; full-page source navigation was rebuilt and visually checked after that regression run. TypeScript/Vite builds passed after repairing a report-dialog syntax error.

New coverage: exact 80% band arithmetic, simultaneous tightening/critical changes, critical flag removal, changed quantities/qualifiers, unique and ambiguous relocation, signed asymmetric/angle/thread/finish parsing, repeated PDF IDs, persistent balloon mapping, chunked-byte enforcement, original evidence preservation, source integrity failure, merge/split, queued report capture/download, workbook preview/commit, optimistic conflict rejection, source-box validation, stale-editor rejection and migration-level snapshot immutability. Early test failures (wrong fixture-count assertion and Windows default temporary-directory permission) were repaired; migration tests now use a workspace-owned temporary directory.

Browser checks confirmed source-linked C27 selection, both revision previews, 80% band reduction, visible score contributors, queued PDF report success and no browser console errors. Desktop split panes were visually inspected at 1440 px; the normal narrow app viewport uses stacked panes. The exported four-page impact report and ballooned drawing were rendered and visually checked. Balloon C27 is numbered 27 in both PDF and workbook. The live fictional demo remains unapproved.

`python scripts/evaluate_engineering.py` generates ten CC0 synthetic challenge PDFs and writes output/evaluation/results.json and RESULTS.md. Exact numeric precision was 6/6 predictions and recall 6/10 expected characteristics, with four false negatives and zero false positives in this small authored corpus. Six comparison scenarios passed. Scans without local OCR, low-resolution scans, limit-only notation and corrupted OCR text were intentionally retained as failed cases. Do not generalize these ratios to industrial drawings. Independent impact-rule precision and human correction rate are NOT_MEASURED.

Actual reports are under output/pdf; rendered page checks are under tmp/pdf-review. No customer data is used. Tests create isolated workspace-owned databases/documents and do not modify the live demo.

## Not verified here

PostgreSQL and Docker were unavailable on the implementation machine. Compose startup, PostgreSQL advisory locks/worker concurrency, TLS issuance, backup recovery, sustained load, malicious parser stress, formal accessibility compliance and independent security review have not been exercised. `.github/workflows/verify.yml` supplies a PostgreSQL service, migration step and test rerun using TEST_DATABASE_URL, but that CI workflow has not been executed here. Never set TEST_DATABASE_URL to a real customer database: the suite provisions test users and controlled records. There is no claim of certified engineering accuracy, production readiness, or validated OCR/GD&T interpretation.

Before a controlled industrial pilot, run the API suite against a separate PostgreSQL fixture setup, add concurrent approval/source-change stress tests and tenant RLS tests if RLS is introduced. Validate extraction against the company's actual golden drawing corpus with measured false positives and missed characteristics. Human completeness review remains mandatory even after those improvements.
# Revision 3 tests

Run `python -m pytest -q` with the project dependencies available. `tests/test_universal.py` adds domain lifecycle, exact arithmetic, source correction, stale-write, tenant, commercial access/grant/revocation, viewer, formula/JSON validation, graph path/cycle/depth, source-tampering, override, queued-report and relationship-import tests. Existing engineering tests remain unchanged.

Final full integration run: 85 passed in 98.99 seconds. After adding the named-reviewer action regression and its permission fix, the final domain run passed 23 tests in 17.33 seconds. There are now 86 covered tests (63 preserved engineering + 23 universal). Report-queue privacy, Excel preview/commit and 80% tolerance-band arithmetic are included. No PostgreSQL/Docker execution was performed on this host.

`python -m scripts.benchmark_graph` records bounded graph performance to `output/graph-benchmark.json`. It does not measure a database or concurrent clients. `python -m scripts.verify_multidomain_reports` generates three fictional reports in each export format and checks every PDF page for content/footer, rendering selected pages for visual review. No industrial accuracy claim follows from these synthetic checks.
