# Known limitations — revision 3

This is a working MVP for evaluation and a controlled pilot. It has not been certified for production release authority or validated against representative confidential industrial datasets.

1. Only engineering, supplier/procurement and quality domain packs are implemented. Other catalog entries are planned.
2. Universal sources are CSV/XLSX/JSON scalar records. Generic PDF/DOCX/PPTX/text/image semantic diff adapters are not implemented. The preserved engineering workbench supports its documented PDF/image/DOCX extraction subset.
3. The UI and register are integrated. Drawing and structured evidence retain specialized schemas and terminal status names. Drawing authority is selected explicitly; historical structured values are not automatically converted into verified characteristics. Commercial drawing workflows and conversion of approved/completed-action records are blocked.
4. Engineering extraction is partial. No reliable native DWG/DXF/STEP/IGES parsing, complete GD&T interpretation, geometric registration or industrial accuracy percentage is claimed.
5. Shared graphs are change-scoped snapshots; no organization-wide versioned asset catalog, shared master-data reconciliation or live ERP/PLM dependency sync exists.
6. Graph paths are bounded and not exhaustive. 1,000-node/5,000-edge map limits apply. In-memory 100,000-edge benchmarking is not a production database/load test.
7. Coverage measures expected relationship types only. Human scope acceptance and evidence can proceed despite declared missing data; this is not proof that all organizational dependencies were found.
8. Freshness is checked at graph import/update with a fixed 90-day threshold; no continuous scheduler rechecks it.
9. Domain approval flows are configuration files, not a policy editor. Admins may sign any one stage; separate humans remain mandatory. Custom conditional quality/CTQ routing is richer in the drawing workbench than the universal engine.
10. Unit conversions, currency validation beyond three-letter form, schema-specific date semantics, full cost modeling and order master validation are not implemented. Associated order value is never reported as loss.
11. Feedback is recorded pending admin review; there is no full feedback-resolution UI or automatic rule learning. Outbox records are not dispatched.
12. Parent IDs and terminal dispositions are implemented, but automatic change chains, bulk/evolution comparisons, alerts/watchers and notification delivery are not.
13. Source/report bytes can use a private filesystem or immutable database storage (the live free pilot uses Supabase, with a 200 MB document budget and 25 MB object ceiling). KMS/object storage, malware scanning, SSO/MFA, RLS, backup drills and independent penetration testing remain deployment work.
14. Sensitive field-name checks do not constitute DLP. Organizations must not upload unapproved HR/medical/legal data into arbitrary labels or text cells.
15. Universal reports support durable queues; job cancellation, fairness, hard resource timeouts and abandoned-job recovery need strengthening. JSON/XLSX carry detailed evidence; PDF graph/drawing visuals are limited.
16. The live backend has been exercised on Render with Supabase PostgreSQL and local Tesseract available there. Automated tests on this Windows host use isolated SQLite unless TEST_DATABASE_URL is set; live health/report checks are not PostgreSQL concurrent-load validation. Free hosting can sleep and has quota limits.
17. The shared register paginates its response after assembling the tenant read model; SQL-native filtering and pagination are needed for enterprise scale.
