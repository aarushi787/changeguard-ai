# Multi-domain demonstration

All PRAGATI INDUSTRIAL SYSTEMS data is fictional and labeled **DEMONSTRATION DATA**. It is not manufacturing, commercial or quality authorization.

## Start

```powershell
$env:PYTHONPATH='.vendor;.' # only when using the supplied local dependencies
python -m alembic upgrade head
python -m scripts.seed_multidomain
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8010 --no-access-log
```

Open http://127.0.0.1:8010. Password for all fictional accounts: `ChangeGuard!2026`.

| Account | Role |
|---|---|
| admin@pragati.changeguard.demo | Admin / manager effectivity |
| engineering@pragati.changeguard.demo | Engineering reviewer |
| quality@pragati.changeguard.demo | Quality reviewer |
| purchase@pragati.changeguard.demo | Purchase reviewer |
| ppc@pragati.changeguard.demo | Production planning reviewer |
| viewer@pragati.changeguard.demo | Read-only |

The seed is idempotent and never overwrites existing tenant records. It is blocked in production unless explicitly enabled for a separate demo deployment. Samples in `samples/multidomain` are synthetic CC0 fixtures.

## Supplier story

Open **Supplier lead time: 7 → 14 days**. Diff shows +7 days/+100%. Impact shows 4 materials, 3 products, 5 orders, 2 customers, 1 Control Plan and 2 operations. Select a customer to inspect the actual relationship path. Associated order values and inventory quantities remain UNKNOWN because the scenario supplies neither.

Evidence: review original/current rows and verify both complete versions. Diff: confirm the change with a rationale. Dependencies: review scope/freshness and record the decision. Actions: complete the five mandatory review tasks with fictional evidence. Approval: use purchase, quality and PPC accounts in order; one person cannot sign twice. Admin then records effectivity. Nothing is sent to suppliers, customers or production systems.

## Engineering story

GS-204 C27 changes ±0.10 to ±0.02 mm. Both tolerance fields are detected; available band arithmetic shows 0.20 → 0.04, an 80% reduction. Impact includes turning, CNC-04, tool T08, CMM, Control Plan, PFMEA, 147 WIP and 82 finished pieces. Capability remains unknown until reviewed. Approvals require engineering then quality.

For the richer drawing viewer, corrections, balloons and PDF extraction, open Drawing workbench. The earlier Northstar tenant remains available with the accounts in DEMO.md; it is not automatically duplicated into PRAGATI.

## Quality story

Inspection interval changes from 100 to 20 with one sample per interval: a 5× interval frequency factor. Review workload, equipment, instructions, cycle time/resources and Control Plan. No cycle-time or cost increase is fabricated. Approvals require quality then engineering.

## Start a new scenario

New change → domain/owner/reason/effectivity → Evidence → upload two files from `samples/multidomain` → compare → review. Import the matching dependency JSON or use the Excel relationship template; imports invalidate analysis, so compare again. Quick mode works without mappings but explicitly exposes unknown coverage and requires a coverage action before approval.

Export a queued PDF/Excel/JSON report from Summary. History retains source corrections, review decisions, actions and approvals. No compliance/HR/production pack is presented as a working fourth domain.
