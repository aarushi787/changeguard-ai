# Universal controlled change

`controlled_changes` is an indexed tenant-owned aggregate. Core columns: id, tenant, domain, status, classification, created, updated, version. The version is used by SQLAlchemy optimistic concurrency and is required as `expected_version` on mutations.

The validated JSON body contains title, description, change type, reason, initiator, owner, mode, effectivity/date/reference, optional parent ID, old/proposed sources, analysis, nodes/edges, actions, approvals, timeline, feedback and internal outbox.

Each source has a label, filename, SHA-256, normalized items and completeness verification. Uploaded files use opaque private storage keys, omitted from API responses. Each item has a stable object/field ID, raw value, normalized value, original value, source row/column, extraction method, engine, confidence and verification. Corrections are separate audited decisions; originals are retained. Replacing a source records an immutable snapshot.

`CHANGE_DELTA`: id, object_id, field, old_value, new_value, type, confidence, engine, old/new provenance, calculated metrics, rules, human decision/reason/reviewer. Numeric-format and repeated-whitespace differences are suppressed. Unknown columns remain text, not inferred engineering measurements.

## State machine

Draft → compared evidence → domain review / actions open → ready for approval → approved → effective → closed. `ANALYSIS_COMPLETE` is recorded as an analysis event; the persisted status immediately reflects the next outstanding review gate. Rejected, superseded and reverted dispositions retain evidence and history.

Approval requires both full sources verified, at least one confirmed real delta, no pending/flagged deltas, dependency-scope review, no truncated graph and all mandatory actions complete with evidence. Missing relationships can be acknowledged only through explicit scope review and completion evidence for the generated coverage action; the UI continues to show missing data. This is human acceptance of limited scope, not automatic proof of completeness.

Each pack specifies at least two independent stages. A different user signs each stage, including when administrators sign. Approvals bind to the evidence digest. Source/map/decision/action edits on unapproved changes clear approvals. Approved sources/actions cannot be edited. A manager explicitly records effectivity; a future date cannot be bypassed. Batch/order/WIP/revision conditions require a reference and human confirmation; no ERP state is queried or changed.

Parent IDs are tenant/access validated. Automatic chains, bulk migrations, rollback execution and effectivity scheduling are not implemented. Revert records a human disposition; it does not undo production activity.
