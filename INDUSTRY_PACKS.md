# Industry overlays

Industries and operational domains are separate concepts. Engineering, supplier and quality workflows share the same core. Existing precision engineering, automotive and fabrication files remain in `industry_packs/` and continue to configure the specialized drawing workbench.

The universal MVP uses domain packs for rules and approval routes. It does not yet compose arbitrary organization-specific industry overlays into universal rules. Future overlays may choose domain bundles, terminology, document types, standards and thresholds. They must not change the requirement for independent human approval or imply compliance certification.

No automotive-specific entity is required by the universal core. A `document` node can represent a Control Plan, quality instruction, process plan or another controlled record. Domain-specific labels belong in configuration and source data.
