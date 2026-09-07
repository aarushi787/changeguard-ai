# AI-off processing pipeline

Universal structured processing:

1. Authenticate, enforce tenant/record access and actual upload limits.
2. Validate CSV, XLSX or JSON; reject formulas, duplicate IDs/headers, invalid fields, nonfinite values and invalid tolerance ordering.
3. Normalize scalar values into stable object/field records with original values and source row/column/hash.
4. Compare matching IDs using deterministic numeric/text normalization.
5. Calculate differences, percentage changes, interval frequency factors and available tolerance bands.
6. Traverse explicitly mapped dependencies with evidence and bounds.
7. Apply versioned domain rules, produce review actions and expose unknowns.
8. Require source, delta and dependency review plus independent human approvals.

Structured extraction reports confidence 1.0 for literal parsing of supported canonical input. This does **not** mean the business data is correct or dependency coverage complete. Human completeness verification remains mandatory. Confidence bands are more detailed in the preserved drawing workbench.

Drawing processing remains staged PDF vector/text extraction → optional local OCR → layout/source location → deterministic engineering parsing → reconciliation/verification → semantic characteristic comparison. It does not invent GD&T interpretation. See AI_MODELS.md for the detailed capabilities and synthetic evaluation misses.

No external model provider is configured or called. AI-off is the implemented mode, not a toggle that quietly falls back to a commercial service. Local Tesseract is optional and is not installed on this Windows host. Private cloud/on-premise deployments can use the same deterministic core. Future providers must explicitly document data handling and retain provenance.

Generic TextDiff, DocumentDiff, ImageDiff and semantic/VLM adapters for the new universal workflow are **not implemented**. PDF/images/DOCX currently belong to the engineering workbench. No PPTX, native CAD, live ERP, PLM or PromiseFlow ingestion is claimed. Existing knowledge retrieval is lexical and provenance-preserving in the engineering module; there is no unrestricted generative chatbot.
