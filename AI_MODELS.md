# Intelligence providers and uncertainty — revision 2

The selected worker is `staged-local-v2`. It makes no external model calls and requires no API key. `backend/providers.py` retains provider interfaces and an explicit test mock. There is no cloud fallback.

## Stages

1. Validate signatures, sizes, decompression bounds and page/image limits.
2. Extract embedded PDF text with unrotated crop-box coordinates and page dimensions. DOCX uses logical text rows; no physical pagination is inferred.
3. When embedded text is absent, optionally invoke local Tesseract if installed (PATH or TESSERACT_CMD). OCR has a 25-second call timeout; the complete extraction subprocess has a 120-second limit. The supplied image installs Tesseract, but that image was not built here. No OCR executable is installed in this Windows evaluation environment.
4. Parse explicitly labeled metadata, symmetric and explicit signed asymmetric tolerances, radii, angles, hole quantity, metric thread and surface-finish tokens. Repeated PDF IDs remain separate uncertain occurrences instead of losing a page. Canonical CSV/XLSX imports retain strict unique IDs and explicit numeric limits.
5. Preserve source page/box/row, raw text, normalized fields, method, heuristic confidence, original extraction and verification status. Completeness is always false until a human confirms it.

Not implemented: geometric registration, arbitrary linework/feature interpretation, reliable limit-only dimensions, arbitrary title-block/revision-history reconstruction, crowded feature association, automatic drawing deskew/orientation selection, native CAD parsing, or complete GD&T frame interpretation. GD&T token recognition is capped at 0.4 and requires a qualified reviewer.

## Confidence and matching

Confidence is an uncalibrated rule-quality indicator, not a probability of engineering correctness. Workbench bands are HIGH_CONFIDENCE at 0.90+, REVIEW_REQUIRED at 0.75–0.89, LOW_CONFIDENCE below 0.75. Every band still requires verification. OCR confidence is capped at 0.89. Human edits retain original evidence and attribution; they do not turn a parser score into an accuracy statistic.

Stable characteristic IDs are matched first. Only unique meaningful label/type pairs with parser-generated page/line IDs receive a fallback match, capped at 0.70 and explicitly labeled review-required. Ambiguous matches stay added/removed. Same numbers do not suppress changed qualifiers, quantity or critical/safety flags. Formatting and source movement remain separate non-engineering results. Decimal interval arithmetic computes old/new band, percentage reduction and tightening factor; shifted intervals are not called tightened merely because their width is smaller.

## Rules

`rules/core.json` (CG-2.0) contains material, tightening, GD&T, CTQ, safety, inventory, supplier, uncertainty and ordinary revision rules. Every recommendation has its rule ID/version, engine, source, reason, confidence and required review. Scores expose every increment and the 100-point cap. Critical/safety flags on either revision remain risk contributors. Actual capability is never invented. Scores prioritize review; they are not Cp/Cpk, failure probabilities or acceptance criteria.

## Retrieval and future providers

Company references use tenant-scoped lexical excerpt retrieval, with filename, hash and source location. No generated answers or invented standards. Embeddings, reranking, source reopening for legacy references and cloud/local VLM integrations are not delivered in this revision. A future provider must retain provenance, enforce a typed schema, record its version/usage, obey private-data policy and keep all human release gates.

## Measured evaluation

Run `python scripts/evaluate_engineering.py`. The ten authored synthetic challenge drawings produced 6 correct numeric characteristics from 6 predictions, with 4 missed characteristics. Six comparison scenarios passed. Scanned/low-resolution inputs without OCR, limit-only notation and corrupted OCR text were missed. This small authored set is not representative industrial validation. Independent impact-rule precision and engineer correction rate are explicitly NOT_MEASURED. See output/evaluation/RESULTS.md and results.json.
