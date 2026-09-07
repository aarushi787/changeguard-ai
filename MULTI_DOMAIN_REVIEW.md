# ChangeGuard AI — multi-domain implementation review

Revision 3, September 2026. Built for **MCCIA AI Applied Studio**.

**Position:** Industrial AI → Change & Impact Intelligence. **Promise:** Know what a change will affect before you approve it.

## 1. Current-system audit

The starting repository was a working engineering MVP, not an empty scaffold. It contained React/TypeScript, FastAPI, SQLAlchemy, Alembic, staged PDF/OCR extraction, characteristic corrections, semantic drawing comparison, deterministic manufacturing rules, tenant-scoped records, dependency mappings, independent approvals and evidence reports. Its 63 existing tests passed after integration. No Git repository/history was available locally.

The system map was: React engineering workspace → FastAPI → PostgreSQL-compatible records and private files → PDF/vector or local OCR extraction → engineering parser → characteristic comparison → manufacturing rules and dependency traversal → engineering/quality review → manager release → evidence reports.

Reviewed boundaries included source files, authentication, audit access, extraction, comparison, rules, graph traversal, migrations, job processing, reports, demo data, frontend, tests, dependency manifests and deployment configuration. Earlier engineering audit findings remain in AUDIT.md and FINAL_REVIEW.md; this document covers the new expansion.

## 2. Gaps and priorities

| Priority | Finding | Disposition |
|---|---|---|
| P0 | All changes assumed a drawing/part and engineering approval route | Added a shared controlled-change model and three independent domain routes |
| P0 | Tenant isolation alone could not protect commercial records from other departments | Added restricted changes and explicit, audited per-change reviewer grants |
| P0 | A new restricted record could leak through the legacy audit feed | Universal events excluded from legacy audit; guarded per-change history and reports |
| P0 | Structured non-drawing revisions had no normalized comparison | Stable IDs, typed fields, exact decimal arithmetic, strict imports and correction history |
| P1 | Graph traversal repeatedly scanned all edges and had no bounded path explanation | Indexed in-memory adjacency, bounded breadth-first traversal, cycle handling and path evidence |
| P1 | Universal effectivity and independent domain approvals absent | Evidence-bound approval sequence, explicit manager effectivity, terminal dispositions |
| P1 | Non-drawing reports and onboarding absent | CSV/XLSX/JSON source templates, relationship import preview, universal queued reports |
| P2 | Full organization object catalog and coverage estimation absent | Change-scoped graphs and honest relationship-type checklist; catalog remains future work |
| P2 | Corporate SSO/MFA, RLS, KMS/object store, backup drills not proven | Documented pilot prerequisites; not represented as completed security certification |
| P3 | Broad regulated and people-domain workflows | Listed as planned; not enabled |

## 3. Architecture changes

| Before | After |
|---|---|
| Drawing change set was the primary aggregate | Indexed `controlled_changes` aggregate plus preserved drawing change sets |
| Industry pack combined manufacturing language and risk settings | Domain packs separate workflow/field/rule logic from industry overlays |
| Manufacturing-only graph cards | Universal impact paths, table view and manual/Excel dependency mapping |
| Engineering/quality approval only | Pack-defined independent routes and separate effectivity decision |
| Engineering reports only | Universal PDF/Excel/JSON with frozen queued report payloads |
| All authorized tenant users could read engineering audit | Restricted universal records require commercial role or a named grant |

The drawing workbench remains available at `/#engineering`. It is intentionally preserved as a specialized module. Universal structured engineering changes use the new workspace; PDF/scan characteristic extraction, bounding boxes, balloons and detailed GD&T token review remain in the workbench. There is not yet an automatic bridge that converts every legacy drawing change set into a universal change.

## 4. Universal model and database

Migration **0003** adds `controlled_changes` and `change_dependencies`, with tenant/domain/status and traversal indexes. The change aggregate stores old/proposed source models, original extraction values, corrections, effectivity, owner, reason, deltas, analysis, graph, actions, approvals and timeline. Version counters reject stale writes. Existing immutable audit and snapshot tables are reused.

Small tenant-scoped records hold rule overrides, named access grants and queued universal reports. No authoritative data is stored in browser localStorage. Detailed schema: DATA_MODEL.md and CHANGE_MODEL.md.

## 5. Domain packs

Available: **engineering**, **supplier/procurement**, **quality**. Pack JSON defines fields, editor roles, independent approval stages, expected dependency types and deterministic rules. New packs using the supported structured field/rule model can be added by configuration and restarting; novel data adapters and specialized workflows still require implementation and tests.

Production, maintenance, compliance, HR, finance and regulated-industry packs are explicitly planned. There is no operational HR decision system or legal-compliance authority hidden behind the catalog.

## 6. Rules and AI pipeline

The shared engine is fully AI-off. Numeric fields normalize with Decimal; whitespace-only and numeric-format differences do not create deltas. Stable row IDs establish matching. Rules emit IDs, point contributions, reasons, source locations and review actions. A lead time of 7 → 14 calculates +7 days / +100%; inspection interval 100 → 20 calculates a 5× interval frequency factor; symmetric tolerance bands 0.20 → 0.04 calculate an 80% reduction.

Scores are conservative review priorities, not failure probabilities. Missing capability, inventory and cost data stay unknown. Recommendation confidence is source confidence, not graph completeness. Ignored/informational detections retain mandatory rule actions to prevent hiding an unresolved high-impact condition.

## 7. Dependency graph

Explicit edges carry evidence. Nodes carry type, owner, freshness date and constrained attributes. Changed object IDs seed traversal. Results provide shortest discovered paths, up to three discovered paths per node, and truncation/cycle metadata. Map columns show hop depth; selecting an entity shows its actual relationships. Paths are not an exhaustive enumeration of every route through a cyclic graph.

Imports validate IDs, duplicate/conflicting entities, endpoints, formulas, row limits and dates. Preview is read-only. Commit replaces the change-scoped map and invalidates previous analysis. The graph is not a global ERP/PLM mirror.

## 8. Security improvements

- Commercial records are excluded from unauthorized lists, detail, source, graph, audit and report endpoints.
- Admins can grant/revoke one named reviewer's access to one change; grants are audited. Standard tenant isolation remains mandatory.
- All universal mutations carry expected versions; independent approval stages cannot be signed by the same person, even an administrator.
- Source files are rehashed for verification, comparison, approval and export. Approved evidence is fingerprinted and preserved.
- Strict file limits, Office archive validation, formula rejection and finite-value validation supplement existing request protections.
- No external model or communication connector is invoked. Outbox events are recorded with `NOT_DISPATCHED` status.

These controls do not replace deployment security review. SECURITY.md lists remaining infrastructure requirements.

## 9. Tests and results

The complete integration run passed **85 tests in 98.99 seconds**. One final named-reviewer action regression was then added; the complete domain suite passed **23 tests in 17.33 seconds**. Together with the 63 preserved engineering tests, the repository now contains **86 passing covered tests**. The last permission refinement touches only the universal action path. Frontend TypeScript and Vite production build passed. Tests use isolated databases, not the demonstration database.

Browser verification: the final supplier report queued and completed successfully (656 ms observed), and the browser console reported no errors. Supplier-to-customer alternate paths were inspected. The 390 px responsive check reported equal document client/scroll widths (375 px), with no page-level horizontal overflow. Sample report covers and delta pages were visually reviewed; all pages were checked for content and footers.

Covered: all three approval lifecycles; missing approval/action gates; same-person denial; original-value preservation; stale edit rejection; tenant isolation; commercial denial/grant/revocation; legacy audit exclusion; source tampering; file/parser rejection; graph cycles, alternate paths and truncation; exact arithmetic; false-positive formatting cases; rule override invalidation; reports.

## 10. Performance evidence

`scripts/benchmark_graph.py` measured approximately 2.1 ms for 100 nodes/1,000 edges, 5.0 ms for 1,000/10,000, and 57.9 ms for 10,000/100,000 on this host. Each traversal was intentionally depth-limited, reached 61 nodes and reported truncation. These figures include in-memory adjacency construction; they do **not** measure PostgreSQL, import throughput or concurrent users. Raw result: `output/graph-benchmark.json`.

## 11. Demonstration and operation

Run migration, seed and server as described in DEMO_GUIDE.md and DEPLOYMENT.md. PRAGATI INDUSTRIAL SYSTEMS contains three explicitly fictional, unapproved scenarios. Supplier lead time reaches four materials, three products, five orders, two customers, one Control Plan and two operations. Engineering includes 147 WIP and 82 finished pieces. Quality includes inspection, equipment, operation and instruction review.

## 12. Known limitations

This is a working evaluation/pilot MVP, not a production-certified industrial authority. Important remaining gaps: universal unstructured-document adapters; unified drawing-to-universal linkage; full enterprise object catalogs and multi-change shared graph editing; organization-specific approval-route UI; richer industry overlays; semantic units/currencies; bulk change chains; notification delivery; outcome administration; graph database/load tests; representative industrial extraction evaluation. Details are explicit in KNOWN_LIMITATIONS.md.

## 13. Next ten highest-value improvements

1. Bridge approved characteristic models and drawing workbench evidence into universal changes without copying away provenance.
2. Add tenant object catalogs with revision-aware relationships and ownership instead of duplicated per-change snapshots.
3. Add source-aligned PDF/DOCX/TableDiff adapters for supplier and quality documents, with measured synthetic and representative evaluations.
4. Add scoped PostgreSQL RLS, foreign-key constraints and least-privilege migration/runtime identities.
5. Add corporate SSO/MFA, access reviews, secret rotation and tested encrypted backup restoration.
6. Add approval-route configuration with separation-of-duty validation and controlled policy revisions.
7. Add graph pagination/lazy database traversal, database benchmarks and real concurrent-user load tests.
8. Add reviewed entity matching, units/currency semantics and import reconciliation against organizational master data.
9. Add outcome review queues and measured false-positive/false-negative feedback without automatic rule modification.
10. Add a transactional integration outbox dispatcher, retries and idempotent ERP/QMS/PromiseFlow connectors with explicit human authorization.
