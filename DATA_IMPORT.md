# Onboarding and data import

Start without ERP/PLM: create a change, choose an available domain, and upload old/new CSV, XLSX or JSON. Download a source template from Domains or Evidence. A stable `id` column matches the same object across versions. Column names use snake_case. JSON is an array of scalar-valued objects.

Examples:

```json
[{"id":"SUP-17","lead_time_days":7}]
```

```json
[{"id":"CP-204","inspection_every_units":100,"inspection_sample_count":1}]
```

Source limits: 2 MB, one worksheet, 1–1,000 rows, up to 40 columns and 5,000 populated fields. Numeric fields reject nonfinite values and invalid signs; inspection intervals must be positive. Formulas are rejected; supply controlled calculated values. Stable IDs and column names are validated. Unknown field names are retained as text without inferred units or business semantics.

## Relationship imports

Dependencies offers a manual entity/relationship builder, JSON map import and Excel/CSV import. Download `/api/v1/imports/templates/relationships?format=xlsx`.

Columns: source_id, source_label, source_type, target_id, target_label, target_type, relation, updated_at, evidence. Each ID must have consistent metadata. Both endpoints must exist. Duplicate edges are rejected. Preview validates and returns counts/freshness; it does not write. Commit replaces the change-scoped graph, preserves audit evidence and invalidates analysis. The expected version prevents committing against changed data.

Nodes require type and ISO date. Edges require a supported relationship and evidence. Connect the changed row ID to the relevant material, process, product, order or document. Node quantity/order value attributes can be added in JSON; order values require a COMMERCIAL change and a three-letter currency.

Dedicated organization-wide Parts/BOM/Employees/Costs master-data imports, fuzzy identity resolution, supplier/part master validation and date/cost semantics for arbitrary columns are not implemented. The generic relationship import supports manual onboarding without pretending to be an ERP master-data connector. People-sensitive structured fields are rejected; field-name checks are not a general DLP guarantee.

## Shared workspace integration — September 2026

For a drawing change use New change → Engineering → Drawing revisions, enter a controlled part number, and upload both revisions inside that record. Supported drawing inputs remain PDF, PNG/JPG, DOCX and canonical characteristic CSV/XLSX; generic policy/PPTX/CAD parsing is not implied. Extraction is queued; verify source characteristics and completeness, then compare. Existing structured engineering changes can explicitly select drawing revisions from Evidence; original structured evidence remains in history and is not automatically converted into verified drawing characteristics.
