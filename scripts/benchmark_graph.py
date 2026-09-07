"""Reproducible CPU graph benchmark, not a database scalability claim."""
import json
import time
from pathlib import Path
from backend.change_engine import AdjacencyGraph

results=[]
for count in [100,1000,10000]:
    nodes=[{'id':str(i),'type':'part'} for i in range(count)]
    edges=[{'source':str(i),'target':str((i+j)%count),'relation':'AFFECTS'} for i in range(count) for j in range(1,11)]
    start=time.perf_counter();result=AdjacencyGraph().traverse(nodes,edges,['0'],depth=6,limit=1000);elapsed=time.perf_counter()-start
    results.append({'nodes':count,'edges':len(edges),'seconds':round(elapsed,6),'reached':len(result['nodes']),'truncated':result['truncated']})
payload={'scope':'In-memory indexing and bounded traversal on this host. Not database, import, or concurrent-user performance.','results':results}
Path('output').mkdir(exist_ok=True);Path('output/graph-benchmark.json').write_text(json.dumps(payload,indent=2),encoding='utf-8');print(json.dumps(payload,indent=2))
