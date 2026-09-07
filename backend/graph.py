"""Typed relational edge adapter; JSON project graphs remain a compatible read model."""
from sqlalchemy import delete
from backend.db import KnowledgeEdge

RELATIONS={('characteristic','operation'):'CHARACTERISTIC_AFFECTS_OPERATION',('operation','machine'):'OPERATION_USES_MACHINE',('operation','tool'):'OPERATION_USES_TOOL',('characteristic','inspection'):'CHARACTERISTIC_INSPECTED_BY',('characteristic','document'):'CHARACTERISTIC_REFERENCED_IN_DOCUMENT',('part','supplier'):'PART_SUPPLIED_BY'}
def typed_edges(nodes,edges):
    types={n['id']:n['type'] for n in nodes}
    return [{**e,'relation':e.get('relation') or RELATIONS.get((types.get(e['source']),types.get(e['target'])),'REQUIRES_REVIEW_OF')} for e in edges]
def persist(s,tenant,project,nodes,edges,actor):
    rows=typed_edges(nodes,edges)
    if len({(r['source'],r['target'],r['relation']) for r in rows})!=len(rows):raise ValueError('Duplicate graph relationships.')
    s.execute(delete(KnowledgeEdge).where(KnowledgeEdge.tenant==tenant,KnowledgeEdge.project_id==project))
    for e in rows:s.add(KnowledgeEdge(tenant=tenant,project_id=project,source=e['source'],target=e['target'],relation=e['relation'],evidence={**e.get('evidence',{}),'confirmed_by':actor}))
    return rows
