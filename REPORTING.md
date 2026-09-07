# Evidence reports

Universal reports support PDF, Excel and JSON. The Summary tab queues a frozen report payload and displays QUEUED/RUNNING/SUCCEEDED/FAILED state. Report status/download re-checks tenant and change-specific access, including revoked commercial grants. The existing database worker processes universal report jobs after pending engineering jobs.

Sections: summary, old/new versions, deltas, calculations, recommendations and rule IDs, score contributors, dependencies, actions, approvals, unresolved gates, complete audit and original/current source values. JSON carries the complete structured payload; Excel has named sheets and formula-safe cells; PDF uses paginated sections and footers. Reports are decision-support evidence, not release certificates.

Uploaded source integrity is verified when the report is queued. Payload and digest remain frozen while later reviews continue. Downloads verify artifact SHA-256. The queued report therefore represents the captured evidence version, not a live view. Failed/abandoned jobs are not automatically retried; queue a new report. Resource hard timeouts, job fairness and cancellation remain future work.

The synchronous report API remains available for small integrations. Use queued reports for the interactive UI. The universal PDF currently emphasizes traceability over compact design; full graph imagery and drawing comparison pages remain specialized engineering-report capabilities.

Fictional sample reports and page renders can be generated with `python -m scripts.verify_multidomain_reports`. They are written to `output/pdf/multidomain`. Existing engineering reports/balloon exports remain available in the drawing workbench.

## Shared workspace integration — September 2026

Reports navigation lists both drawing and structured changes. Open a drawing change and use Export report to queue PDF/XLSX/JSON evidence. The queued report includes the linked original proposal and integration audit events. Generic report generation is rejected for a linked drawing change to avoid exporting obsolete structured analysis as current evidence. Earlier immutable exports remain historical artifacts.
