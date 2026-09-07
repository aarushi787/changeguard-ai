# Deterministic impact rules

The universal engine is `backend/change_engine.py`. It uses no LLM and performs arithmetic with Decimal. Rules come from domain pack JSON. Supported conditions: field changed, numeric increase, numeric decrease. Each rule defines a stable ID, integer points and explicit review topics.

Example: `SUP-LEAD-001`, lead_time_days increase, +35 points, reviews open purchase orders, production schedule, customer commitments, inventory coverage and alternative supply. Recommendations cite object/field values and old/new source locations. They request verification rather than assert shortages, capability or financial losses.

Scores sum field-rule contributions plus mapped inventory/customer/supplier exposure and low-confidence review increments, capped at 100. Severity thresholds: ≥80 critical; ≥50 high; ≥25 moderate; positive below 25 minor; zero informational. This is a configurable review-priority heuristic, not a probability or validated process capability model. A change affecting two tolerance fields receives two visible field contributions; the report does not hide this aggregation.

Tenant administrators can override known rule point values from 1–100 through Settings/API. Rules cannot be disabled with zero points. Saving overrides invalidates analysis and approvals on open universal changes; approved evidence remains frozen. The override values, reason and new analysis evidence are audited.

Ignored and informational detections retain conservative recommendations and mandatory review actions. Reviewers document why an action is unnecessary before completing it; false-positive feedback never silently changes a rule. Organization ignore patterns, conditional logical expressions, universal CTQ semantics and custom approval policy editors are not yet implemented. The legacy drawing engine retains its richer CTQ/safety and GD&T-specific rules.
