# Domain packs

Available pack files: `domain_packs/engineering.json`, `supplier.json`, `quality.json`. The supplier pack includes procurement review. Planned domains are disclosed by `/api/v1/domain-packs` and cannot be selected as implemented workflows.

Pack fields: id, name, version, status, description, edit_roles, approvals, required_relationship_types, fields and rules. An approval stage is a list of permitted role alternatives. Pack loading requires at least two nonempty stages and validates supported rule operators/points. Core domain IDs are discovered from AVAILABLE JSON files on startup; a restart is required for a newly installed pack.

| Pack | Route | Example |
|---|---|---|
| Engineering | ENGINEER/ENGINEERING → QUALITY | tolerance/material specification |
| Supplier | PURCHASE → QUALITY → PLANNER/PPC | lead time/price/material |
| Quality | QUALITY → ENGINEER/ENGINEERING | inspection interval/method |

ADMIN can act in a stage but cannot sign multiple stages on the same change. Read-only users cannot mutate. Named commercial grants allow a quality or production reviewer to see the restricted evidence without granting company-wide commercial access.

New domain logic using scalar fields and supported condition operators can be installed as a pack without editing the rule engine. An adapter, novel field semantics, a new action type or specialized regulated workflow requires implementation, security review and evaluation. The three supplied onboarding templates are explicitly curated; a new pack must supply its own tested onboarding conventions.

Planned: supply chain, production, maintenance, compliance, HR, finance, product, IT, pharma, food, electronics, textile, packaging and chemical. No clinical, legal or employment decisions are implemented.
