# Demonstration walkthrough

## Fictional scenario

**DEMONSTRATION DATA** throughout. Northstar Precision Works and Aster Industrial Systems are fictional. Sample geometry is schematic and is never a manufacturing instruction.

Gear Shaft GS-204, drawing DWG-GS-204:

- Revision C: bearing seat characteristic C27, diameter 20 mm, tolerance ±0.10 mm.
- Revision D: the same nominal with ±0.02 mm tolerance.
- Tightening factor: (0.10 - (-0.10)) / (0.02 - (-0.02)) = **5×**.
- Parser extraction confidence: **90% rule-level confidence**, not a calibrated probability. Every characteristic still requires human verification.
- Seeded critical flag plus recorded inventory exposure produces CRITICAL prioritization under the demonstration pack. This is not a measured manufacturing risk probability.
- Linked feature, OP30 CNC turning, CNC-04, finish insert T08, soft jaws FX-12, CMM procedure IP-204, Control Plan CP-021, PFMEA PF-021, Work Instruction WI-030, customer.
- **147 fictional WIP units and 82 fictional finished units**, total 229.
- Machine capability is **UNKNOWN**. Nothing in this demo establishes CNC-04's ability to meet the revised tolerance.

The revision title-block change C -> D is separately detected. It may be accepted as an administrative change or rejected as irrelevant to the engineering impact scope with a recorded reason; that does not dismiss the tolerance change.

## Quick tour

1. Open the local application and use the prefilled engineer login.
2. Dashboard: inspect 1 open change, 1 critical change, 147 WIP units and 3 pending document reviews.
3. Select **Explore impact** or the change register row. Click machine/tool/document nodes to inspect why they appear.
4. Open **Drawing Comparison**. Click the C27 highlight. Inspect old/new values, tightening, extraction confidence and the capability-verification requirement. Zoom/pan and page selection operate on actual source images.
5. Open **Characteristics**. Each source characteristic is REVIEW_REQUIRED. Verify/edit against the controlled source and enter the rationale. New manual characteristics may be added for unparsed requirements. Confirm source completeness for both revisions only after a full drawing review.
6. Open **Impact Map → Edit & verify dependency map**. Check actual directed relationships, add any missing dependencies, explain the evidence and confirm scope. The JSON editor validates node references. In this fictional scenario, a test reviewer can document that they reviewed the fixture map; this is not a real engineering sign-off.
7. Re-run impact analysis after source/map edits. This clears old approvals and detection/document review decisions and regenerates automatic capability/scope actions.
8. Review each detection as accepted/false-positive/flagged with evidence. Resolve flags before approval.
9. In **Affected Documents**, record controlled document review or justified non-applicability. Actual CP/PFMEA content lives in the organization's document system; this demo records references and decisions.
10. In **Actions**, assign new reviews or complete assigned reviews with test evidence. The action owner or manager/admin must complete each action. To complete the seeded quality action, sign in as quality or manager.
11. In **Approvals**, satisfy the displayed gates, then approve engineering as engineer@changeguard.demo.
12. Sign out; sign in as quality@changeguard.demo and approve quality. The server rejects same-user double approval.
13. Sign in as manager@changeguard.demo to explicitly release. The released source/change evidence becomes immutable through the API.
14. Export the impact PDF/Excel workbook and inspect the **Audit Trail** for the recorded evidence, corrections, reviews and approvals.

All five demo accounts use `ChangeGuard!2026`. Seed is idempotent; rerunning it does not reset your review progress. To start over, create a new project/revisions or use a separate fresh evaluation database. Do not delete audit history to reset a workflow.

## Your own test comparison

Create a company or a project in the demo tenant. Upload `samples/characteristics-A.csv` and `samples/characteristics-B.csv` with revision labels A and B. Wait for READY jobs, then use **New engineering change**. This deliberately exercises the exact supported import schema. `samples/inventory.csv` applies only to part GS-204; update it to match a new controlled part before import.

Reference library accepts the authored PDFs as test references. Searching `Material` returns the source excerpt and page/hash. There is no generated answer or hidden cloud provider.

The original PDFs/CSV fixtures are CC0. Supporting report and balloon outputs can be reproduced with `python -m scripts.verify_reports` after seeding.

## Revision 2 workbench walkthrough

Open Characteristics, select C27 and choose revision C/D. Confirm the purple source region and persisted balloon #27. Filter confidence below 90% to find uncertain metadata. Edit values with a reason, or verify/reject/flag; originals remain visible. Merge/split prepares new characteristic IDs and retains superseded records. Replacements require separate verification. Annotation edits invalidate existing analysis/approvals.

Drawing Comparison uses old source / selected change / new source panes. C27 displays 0.20 → 0.04 mm, 80% reduction and CG-TOL-004. Rule evidence shows +50 tightening, +20 critical and +10 stock exposure in the fictional dataset; the 80/100 priority meets this pack's CRITICAL threshold. It is not a failure probability.

Projects & drawings → Import process / quality map provides downloadable templates and a preview before saving. Existing identifier labels/types must agree; adapt templates to your project. Imported graphs remain unconfirmed until an engineer reviews completeness.

Export report queues an evidence snapshot and displays QUEUED/RUNNING/SUCCEEDED. Download PDF, workbook or JSON after completion. No actual engineering approvals were granted by the implementation agent in the live demonstration dataset. Automated tests exercise approval logic with explicitly synthetic test users in isolated test databases.
