# Dependency graph

The graph interface is `GraphProvider.traverse(nodes, edges, starts, depth, limit)`. The current implementation builds adjacency lists in O(V+E), then performs bounded breadth-first traversal. Cycles do not cause recursion or infinite traversal. Returned nodes include up to three discovered paths. Only the first shortest path is expanded; the result is not an exhaustive path enumeration.

Change-scoped nodes are retained in the controlled aggregate. Edges also persist in `change_dependencies`, with a tenant/change/source index and a uniqueness constraint across tenant, change, source, target and relationship. This is a relational implementation; no Neo4j dependency is installed.

Supported relations: AFFECTS, DEPENDS_ON, USES, REQUIRES, OWNED_BY, SUPPLIED_BY, REFERENCED_BY, APPROVED_BY, IMPACTS. **Direction always follows potential impact in the entered map.** The MVP does not automatically invert DEPENDS_ON/SUPPLIED_BY; enter the intended impact direction and cite evidence. UI and import preview call this out.

Source row IDs must match graph node IDs. A supplier row `SUP-17` seeds paths to materials, products, orders and customers. Disconnected nodes are not declared affected. Every edge requires evidence; nodes require freshness dates. Dates older than 90 days are flagged at import/update. The freshness threshold is currently fixed, not continuously recalculated by a scheduler.

Limits: 1,000 nodes and 5,000 edges per controlled map; 1,000 spreadsheet relationship rows; traversal default depth 6, API depth 1–8, maximum 1,000 returned nodes. Truncation blocks approval. The map UI displays shortest-path depth columns and actual paths on selection; adjacent cards are not assumed connected.

Coverage is a count of expected **relationship types** present versus those in the selected pack. It is not an enterprise readiness percentage. Unknown inventory and commercial exposure are not converted to zero. Values in different currencies are never added together; associated order value is not loss.

Run `python -m scripts.benchmark_graph` for an in-memory benchmark including 100,000 edges. This does not bypass per-change import limits or establish database production capacity. Lazy database traversal, organization-wide shared object catalogs and concurrent-user benchmarks remain future work.
