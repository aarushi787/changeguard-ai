# ChangeGuard AI

## Revision 3 — Industrial AI · Change & Impact Intelligence

**Know what a change will affect before you approve it.** Built for MCCIA AI Applied Studio.

The default workspace now supports three working domains: **engineering, supplier/procurement and quality**. It includes controlled source versions, corrections, deterministic comparison, evidence-backed impact paths, review actions, independent approvals, effectivity and PDF/Excel/JSON reports. The established drawing workbench remains available at `/#engineering`.

Start with [DEMO_GUIDE.md](DEMO_GUIDE.md). The new fictional tenant is **PRAGATI INDUSTRIAL SYSTEMS**; sign in as `admin@pragati.changeguard.demo` with `ChangeGuard!2026`. Run `python -m alembic upgrade head` and `python -m scripts.seed_multidomain` before using it. Existing Northstar data and accounts are preserved.

Read the [multi-domain audit and implementation review](MULTI_DOMAIN_REVIEW.md), [domain model](CHANGE_MODEL.md), [domain packs](DOMAIN_PACKS.md), [import guide](DATA_IMPORT.md) and [known limitations](KNOWN_LIMITATIONS.md). This is a working pilot MVP, not production-certified manufacturing authority. Unimplemented domains are visibly planned; external AI is disabled.

The sections below describe the preserved engineering module and earlier revision history.

**Detect Changes. Understand Impact. Prevent Manufacturing Mistakes.**

A working engineering revision and release-intelligence MVP, audited and revised for MCCIA AI Applied Studio. Initially built from an empty repository with React 19, TypeScript, Vite, React Query, FastAPI, SQLAlchemy, Alembic and a PostgreSQL deployment configuration. The application is private by default: no drawing contents are transmitted to external AI providers.

## Start here

The locally built application is served at **http://127.0.0.1:8010** while the local server is running. Restart it with `scripts/start-local.ps1`. Fresh installation instructions are in [SETUP.md](SETUP.md).

Demo accounts all use `ChangeGuard!2026`:

| Account | Role |
|---|---|
| engineer@changeguard.demo | Engineering reviewer |
| quality@changeguard.demo | Independent quality reviewer |
| manager@changeguard.demo | Administrator / release manager |
| planner@changeguard.demo | Production planner |
| viewer@changeguard.demo | Read-only |

**DEMONSTRATION DATA:** Northstar Precision Works, GS-204 drawings, customers, machines, tooling and quantities are entirely fictional. The drawings are schematic software fixtures and must never be used for manufacture.

## Implemented workflow

1. Sign in or create a company; company registration creates its administrator.
2. Create a project with a controlled part number.
3. Upload old and new revisions. Durable database jobs extract supported information.
4. Compare ready revisions and inspect source text/image locations.
5. Correct or manually add characteristics; verify each and confirm source completeness.
6. Edit and confirm the dependency map. Re-run analysis after source, graph or inventory edits.
7. Explore the **Manufacturing Blast Radius** and evidence-backed impact reasoning.
8. Accept, reject as false positive, or flag each detection with a rationale.
9. Review affected documents and assign/complete actions. Generated actions call for capability verification where needed.
10. Approve engineering, then approve quality using a different account.
11. A manager explicitly releases the revision. Released evidence cannot be edited through the API.
12. Queue PDF, Excel or JSON evidence reports and inspect the complete source/project/change audit history.

All authoritative state lives in the database. There is no localStorage-based industrial data store. Browser memory is cleared on sign-in/sign-out through a full reload.

## Revision 2 improvements

- Source-linked verification workbench with confidence filters, original extraction, corrections, verify/reject/flag, manual entry and merge/split.
- Stable balloon mappings, collision-aware initial placement, manual positioning, leader lines and matching PDF/Excel exports.
- Multi-stage embedded PDF text/layout, optional local OCR, signed asymmetric tolerances, angles, hole quantities and thread/finish tokens.
- Semantic comparison preserves changed qualifiers and CTQ/safety flags; exact interval arithmetic produces band reduction and tightening factor.
- Versioned rule evidence explains WHY, SOURCE, CONFIDENCE and ENGINE, including visible score increments.
- Typed dependency relationships and process/Control Plan/PFMEA Excel templates with preview-before-import.
- Actual-byte upload limits, source rehashing, bounded extraction subprocesses, optimistic version checks, approval fingerprints and immutable release snapshots.
- Queued evidence reports and a reproducible synthetic evaluation with explicitly reported misses.

The full audit, implementation disposition, architecture comparison and next ten improvements are in [FINAL_REVIEW.md](FINAL_REVIEW.md). Baseline findings: [AUDIT.md](AUDIT.md).

## Explicit limitations

This is a **working MVP for evaluation and controlled pilot development**, not a certified production manufacturing authority.

| Area | Current boundary |
|---|---|
| OCR / vision | Optional local Tesseract adapter; no executable installed on this Windows host. Docker image includes it but is untested here. No geometric registration or automatic linework diff. |
| CAD | DWG, DXF, STEP and IGES are rejected; future adapters only. |
| GD&T | Recognizes selected Unicode tokens / datum and modifier words. Does not interpret feature-control frames, standards, datum precedence or conformance. Always human review. |
| Drawing coverage | Explicit symmetric/signed-asymmetric expressions, angles, metadata and selected callout tokens. Limit-only dimensions, general layouts and full feature interpretation remain incomplete. Ambiguous matching requires human reconciliation. |
| BOM | Canonical characteristics can be imported; arbitrary BOM schemas, quantity reconciliation and supplier part matching are not implemented. |
| Risk | A configurable ordinal prioritization score, not a failure probability or certified capability conclusion. |
| Graph editing | Typed relationships, workbook templates and JSON editor; no arbitrary legacy workbook understanding or live synchronization. |
| Industry packs | Terminology/document catalog and risk thresholds exist. The safe two-reviewer release order is fixed; arbitrary workflow designers and industry-standard validation are not implemented. |
| Knowledge / RAG | Lexical excerpt retrieval only. No embeddings, semantic reranking or generated answers. |
| Integrations | Versioned API, no live ERP/PLM/MES/QMS connectors. |
| Reports | UI exports use snapshot-backed jobs; legacy synchronous API remains. No hard report timeout or large-history load test. Source previews show first-page excerpts. |
| Storage | Private local/volume storage, opaque expiring download tokens. No S3/KMS adapter or application-level encryption at rest. Use encrypted infrastructure. |
| Enterprise security | No SSO/MFA, password recovery, antivirus, SIEM exporter, PostgreSQL RLS or formal penetration test. Deployment hardening is required. |
| Database verification | Local integration tests use SQLite. PostgreSQL SQLAlchemy models and migrations are provided, but PostgreSQL/Docker were unavailable on the implementation machine. Container startup and concurrent PostgreSQL behavior have not been verified here. |

## Documentation

- [SETUP.md](SETUP.md): installation and running locally
- [DEMO.md](DEMO.md): fictional scenario and walkthrough
- [ARCHITECTURE.md](ARCHITECTURE.md): components and design decisions
- [DATA_MODEL.md](DATA_MODEL.md): persisted aggregates and evidence schemas
- [API.md](API.md): endpoint inventory and examples
- [AI_MODELS.md](AI_MODELS.md): deterministic behavior, confidence and provider boundaries
- [SECURITY.md](SECURITY.md): guarantees, role matrix and deployment obligations
- [TESTING.md](TESTING.md): test commands, coverage and validation results
- [DEPLOYMENT.md](DEPLOYMENT.md): PostgreSQL, containers, TLS, backup and operations

The original sample PDF and CSV files under `samples/` are CC0 fictional fixtures. Dependency licenses remain those of their respective projects.
