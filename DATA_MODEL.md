# Data model — migration 0002

PostgreSQL is the deployment database; SQLite is the local evaluation adapter. IDs are UUID hex, times are UTC. Tenant queries and role checks are enforced in the API. There is no database RLS or complete foreign-key normalization.

| Table | Purpose |
|---|---|
| organizations | Company and industry pack |
| users | Tenant identity, scrypt password, role |
| sessions | Hashed opaque cookie and expiry |
| records | Tenant-scoped JSON aggregates; integer optimistic `version` |
| knowledge_edges | Tenant/project/source/target/relation, import/confirmation evidence; unique relationship tuple |
| audit_events | Append-only actor, entity, operation, original/edited evidence and time |
| evidence_snapshots | Immutable entity/stage/data/digest/time; extraction and complete release evidence |

Migration 0002 adds the version column and two new tables. It installs snapshot update/delete prevention triggers for SQLite/PostgreSQL. Migration 0001 supplies audit triggers. ORM listeners provide additional protection. A database owner can disable triggers: this is not tamper-proof storage against a privileged administrator. Destructive downgrade is disabled.

## Aggregates

Project: part/customer/name, nodes, typed edges, graph_verified. Revision: private storage key, source hash, status, filename, revision label, characteristics, metadata, pages, warnings, pipeline, completeness_verified. Change set: source/target IDs, changes with embedded source evidence and dependency-edge snapshot, risk, inventory snapshot, documents, actions, comments, approvals, stale/status, release_snapshot_id/release_digest. Inventory imports replace the project's current snapshot; analyzed changes retain their own snapshot. Empty exposure is unknown, not evidence of zero stock.

Jobs: extraction or REPORT, status/timing/provider/failure; report jobs capture private payload/audit/source revisions and artifact hash. Status APIs omit payload, event bodies and storage keys. Knowledge records retain reference hash and located chunks. Download-token records hold only hashed token, owner/revision and expiry.

## Characteristics

Required evidence: characteristic_id, type, label, nominal/upper_tolerance/lower_tolerance/unit or textual raw value, source_page, source_location (page/bbox/row), confidence, extraction_method, verification_status. Revision 2 adds normalized representation, confidence_band, engine, extracted_original, human_corrections, balloon_number, inspection_reference and optional balloon_position. Quantity, thread, surface_finish and GD&T tokens exist where recognized. Page dimensions describe PDF points or image pixels; DOCX uses logical rows without invented layout.

Edit/verify preserves extracted_original and appends attributed correction evidence. Rejection retains the characteristic. Merge/split marks originals SUPERSEDED and adds new unique IDs with derived_from references and REVIEW_REQUIRED status. Neither operation deletes original evidence. Stable balloon numbers are independent of list order; issued numbers remain reserved even on rejected/superseded evidence. Manual renumber rejects collisions; manual positions must lie on the page.

## Comparison and release evidence

Each change includes old/new snapshots, classification, matching method, confidence, Decimal-derived metrics, risk contributors, rule recommendations, impacted nodes/edges and human review. `comparison_model` also returns UNCHANGED, MOVED and VISUAL_ONLY results; those do not become engineering changes automatically.

Approvals record user/stage/time/reason plus evidence_digest. Quality/release must refer to the same fingerprint as engineering. Final release adds an immutable snapshot of the entire decision context. Current project mapping can evolve without rewriting the released change's embedded analysis. Source/hash integrity failures block extraction, viewing, reports and approval.

Typed graph rows and project JSON remain a compatible pair of write/read models; historical JSON edges are typed on edit/import. Machines, tooling, PFMEA/Control Plan references and suppliers remain graph node types, not falsely claimed fully normalized systems of record.
# Revision 3 additions

Migration 0003 adds `controlled_changes` (tenant/domain/status/classification, versioned JSON evidence, timestamps) and `change_dependencies` (tenant/change/source/target/relation/evidence). Composite indexes support tenant/domain listings and source-edge traversal; duplicate edges are constrained. Existing engineering tables are retained unchanged.

Source versions, deltas, reviews, actions, effectivity and approvals are validated aggregate fields described in CHANGE_MODEL.md. Named commercial grants, domain point overrides and universal report jobs use typed Record kinds `change_access`, `domain_settings` and `universal_report`. Universal audit events carry scope metadata and are excluded from the legacy audit listing; guarded universal history enforces record-specific access. Existing append-only triggers protect audit/snapshot history after migrations.

Tenant isolation is enforced in application queries. Database RLS, normalized global asset catalogs and additional foreign keys remain future hardening; do not infer them from the presence of tenant IDs.

## Shared workspace integration — September 2026

The integration adds validated references inside existing versioned aggregates rather than new tables: controlled_changes.data.drawing_project_id → project; project.data.controlled_change_id → controlled change; change_set.data.controlled_change_id → controlled change. The workspace adapter deduplicates linked records. These references are enforced by application services, not physical foreign keys. Document blobs still use schema migration 0004.
