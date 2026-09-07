# Expert audit — ChangeGuard AI baseline

Audit scope: every source module, API, models, migration, rule pack, frontend component/style, tests, deployment/configuration, fixtures, report generator and operating document. Existing browser inspected. No Git repository/history is present. Baseline is v0.1.0; modifications began only after this inspection.

## Current system map (before)

React single-file workspace → FastAPI single application module → SQLAlchemy JSON aggregates and private files → embedded-text regex extraction / image manual entry → no active AI or OCR → exact-ID numeric/text comparison → untyped graph traversal and hard-coded risk increments → reasoned review + two-person approval → synchronous PDF/XLSX.

## Trust and adoption verdict

Useful as a constrained demonstration, not ready for unsupervised real drawing analysis or confidential customer production deployment. Confidence values describe hand-set parser heuristics, not measured accuracy. Human gates exist but engineering matching, source workbench, imports and failure handling leave too much manual reconstruction. A Quality Head can inspect decisions, but cannot yet trace each recommendation to a versioned rule or inspect reproducible release snapshots. A small supplier would need to author JSON rather than import its existing process/quality sheets.

## Prioritized findings

| ID | Priority | Finding / consequence | Evidence |
|---|---|---|---|
| CG-001 | P0 | Equal nominal/tolerance suppresses other raw callout changes; quantity, thread/detail or CTQ-only change can disappear. | intelligence.compare equality shortcut and field list |
| CG-002 | P0 | Exact-ID-only matching turns relocated fallback IDs into removals/additions; no ambiguity handling or matching provenance. | intelligence.compare |
| CG-003 | P0 | Worker has no execution fencing or timeout. Retried RUNNING work can overwrite newer evidence; SQLite has no row-level write lock equivalent. | main.process_one/retry_job |
| CG-004 | P0 | Critical low-confidence verification is gated only via completeness booleans; no source-version fingerprint on approval. | main.blockers/transition |
| CG-005 | P0 | Request limit checks claimed Content-Length only; chunked bodies can be fully spooled before application file checks. | main.boundary/upload |
| CG-006 | P0 | No asymmetric/limit/angle/thread/hole/finish parsing; repeated metadata IDs fail entire multi-page extraction. No OCR implementation. | DeterministicProvider |
| CG-007 | P0 | No drawing beside verification table; no reject/merge/split or reliable manual source location. | Characteristics tab |
| CG-008 | P1 | Balloon numbering derives from array order, not a persisted mapping. No collision avoidance/leaders or manual position. | reports.balloon_export |
| CG-009 | P1 | Risk score increments hidden in code; generic recommendation text omits rule ID/version, evidence and engine. | assess/generated_actions |
| CG-010 | P1 | Graph edge meaning absent; graph authoring requires JSON; traversal misses semantics and displayed arrows can imply relationships not present. | GraphInput/BlastRadius |
| CG-011 | P1 | Empty inventory presents 0 rather than unknown; order/supplier exposure not distinguished. | dashboard and inventory aggregations |
| CG-012 | P1 | Reports omit cover, drawing evidence, explicit unresolved gate list and JSON export; generation is synchronous. | reports.make_report |
| CG-013 | P1 | Released graph can change later; no immutable whole-release snapshot. Audit protects rows but app DB owner can disable triggers. | graph/transition/migrations |
| CG-014 | P1 | Production credentials share schema-owner privileges; SSO/MFA, malware scanning, disk encryption, backup restore and PostgreSQL deployment unvalidated. | Compose/security docs |
| CG-015 | P1 | Source files not rehashed before extraction/display; corrupt or replaced file could differ from recorded evidence. | file/page/worker |
| CG-016 | P1 | No measured evaluation dataset beyond simple self-authored fixtures; passing unit tests do not establish extraction accuracy. | tests/samples |
| CG-017 | P2 | RAG excerpts have provenance but source cannot be reopened; all matching is substring overlap. | knowledge routes/UI |
| CG-018 | P2 | Monolithic UI/API, broad `any`, unpaginated large aggregate fetches, no persisted workbench selection/role affordances. | src/main.tsx/main.py |
| CG-019 | P2 | No process/Control Plan/PFMEA Excel onboarding templates; no preview-before-import. | projects UI |
| CG-020 | P3 | No CAD, advanced VLM, embeddings or live ERP integrations; appropriately disclosed but not implemented. | capabilities/providers |

## Implementation policy

Preserve the controlled revision→impact→human release workflow. Fix P0 evidence integrity and deterministic detection first. Add explicit confidence/matching uncertainty, persisted annotations, typed graph imports, versioned recommendations, a source workbench, traceable reports and measured synthetic evaluation. No LLM arithmetic, invented machine capability, automatic release, or standards conformance claims. Remaining deployment gaps must stay explicit even after implementation.

## Implemented disposition (revision 2)

| Findings | Disposition |
|---|---|
| CG-001 | Fixed: raw qualifiers, quantities and critical/safety changes survive numeric equality; simultaneous tightening remains classified correctly. |
| CG-002 | Mitigated: unique generated-ID label/type fallback with 70% confidence cap; ambiguous matching stays explicit. Spatial matching remains future work. |
| CG-003 | Mitigated: bounded extraction subprocess, optimistic record conflicts, released/reviewed retry guards. PostgreSQL concurrency stress remains unverified. |
| CG-004 | Fixed for application workflow: source-bound approval digests, stale-editor source version checks, release snapshot. Privileged DB tampering remains out of scope. |
| CG-005 | Fixed: actual request-byte limit before multipart parsing, including chunked bodies. |
| CG-006 | Partially addressed: staged vector/layout/local OCR adapter, signed asymmetric/angle/thread/finish/quantity support, repeated ID retention. Real OCR validation, limit dimensions, GD&T and geometric understanding remain gaps. |
| CG-007 | Implemented: split-pane source workbench, original/corrected history, verify/reject/flag/manual add/merge/split and source coordinates. |
| CG-008 | Implemented: persistent unique numbers, source association, collision-aware initial positions, manual move/renumber and matching exports. Manual placement can still overlap and must be reviewed. |
| CG-009 | Implemented: configurable rule IDs/version, sources, reasons, confidence, score increments and mandatory rule-linked actions on new/reanalyzed changes. |
| CG-010 | Partially addressed: typed relational edges, actual relationship evidence and workbook imports. A visual graph authoring tool remains future work. |
| CG-011 | Partially addressed: empty change-register/detail exposure is UNKNOWN. Complete inventory coverage and purchase/production-order integrations remain unavailable. |
| CG-012 | Implemented: queued snapshot-backed reports, cover/readiness, first-page drawing excerpts, rules and JSON export. Large-history load and hard report timeouts remain gaps. |
| CG-013 | Implemented: immutable release context and database snapshot triggers. Schema-owner/runtime separation remains an operational requirement. |
| CG-014 | Open: production infrastructure/security validation is not claimed. |
| CG-015 | Implemented: rehash extraction, rendering, download, report and approval sources. |
| CG-016 | Partially addressed: reproducible ten-drawing challenge and six comparison cases with explicit misses. Independent representative evaluation remains open. |
| CG-017 | Open: lexical retrieval remains limited; no new generic chatbot or invented standards. |
| CG-018 | Partially addressed: engineering workspace split into its own module, stale-source checks and role-aware approval controls. Aggregate pagination/stronger frontend typing remain open. |
| CG-019 | Implemented: process/Control Plan/PFMEA canonical relationship workbooks with preview/commit, row/hash provenance and conflict validation. Arbitrary legacy templates are not interpreted. |
| CG-020 | Explicit future scope: no CAD, advanced AI or live enterprise connectors claimed. |

See FINAL_REVIEW.md for the requested fourteen-part review and prioritized next ten improvements. This audit is a technical implementation review, not engineering certification or a security attestation.
