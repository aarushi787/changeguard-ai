"""One workspace register; each change retains exactly one approval authority."""
from datetime import timezone
from fastapi import APIRouter, Depends, HTTPException
from pydantic import Field
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.db import Record, User
from backend.main import db, user, require, get, records, add, audit, blockers
from backend.universal import query, view, get_change, mutable, Mutation, patch, event
from backend.evidence import snapshot

router = APIRouter(prefix='/api/v1/workspace', tags=['Unified workspace'])


def drawing_view(s, u, project, change=None, parent=None):
    d = change.data if change else {}
    changes = d.get('changes', [])
    levels = ['UNKNOWN', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    risk = max((x['risk']['level'] for x in changes), key=lambda x: levels.index(x), default='UNKNOWN')
    actions = [{**a, 'owner': a.get('owner_id', ''), 'owner_name': a.get('owner', ''),
                'mandatory': True} for a in d.get('actions', [])]
    row = parent or change
    issues = blockers(s, u, change) if change else ['Upload and compare two drawing revisions.']
    return {
        'id': row.id, 'version': row.version, 'workflow': 'DRAWING', 'domain': 'engineering',
        'title': parent.data['title'] if parent else d['title'], 'change_type': 'DRAWING_REVISION',
        'classification': 'INTERNAL', 'status': d.get('status', 'DRAFT'),
        'owner': parent.data['owner'] if parent else '',
        'effectivity': project.data.get('effectivity', 'IMMEDIATE'),
        'effective_date': project.data.get('effective_date'),
        'effectivity_reference': project.data.get('effectivity_reference', ''),
        'ready_for_approval': bool(change and not issues and d.get('status') not in {'APPROVED','RELEASED'}),
        'created': row.created.replace(tzinfo=timezone.utc).isoformat(),
        'demo': parent.data.get('demo', False) if parent else d.get('demo', False),
        'actions': actions, 'approvals': d.get('approvals', []),
        'analysis': {'level': risk, 'score': max((x['risk'].get('score', 0) for x in changes), default=0),
                     'score_policy': 'Highest characteristic review score; not a sum or probability'} if change else None,
        'blockers': issues,
        'drawing': {'project_id': project.id, 'change_set_id': change.id if change else None,
                    'controlled_change_id': parent.id if parent else None},
    }


def all_changes(s, u):
    projects = {r.id: r for r in records(s, u, 'project')}
    comparisons = records(s, u, 'change_set')
    parents = s.scalars(query(u)).all()
    linked = {p.data['drawing_project_id']: p for p in parents if p.data.get('drawing_project_id')}
    rows = [{**view(p), 'workflow': 'STRUCTURED'} for p in parents if not p.data.get('drawing_project_id')]
    for project_id, parent in linked.items():
        project = projects.get(project_id)
        if not project: raise HTTPException(409, 'Drawing project reference is unavailable.')
        comparison = next((c for c in comparisons if c.data['project_id'] == project_id), None)
        rows.append(drawing_view(s, u, project, comparison, parent))
    for comparison in comparisons:
        project = projects.get(comparison.data['project_id'])
        if project and not project.data.get('controlled_change_id'):
            rows.append(drawing_view(s, u, project, comparison))
    return sorted(rows, key=lambda x: (x['created'], x['id']), reverse=True)


@router.get('/changes')
def listing(offset: int = 0, limit: int = 200, u: User = Depends(user), s: Session = Depends(db)):
    if offset < 0 or not 1 <= limit <= 200: raise HTTPException(422, 'Page limit must be 1–200.')
    return [{k:v for k,v in row.items() if k not in {'sources','nodes','edges','timeline','feedback','outbox'}}
            for row in all_changes(s, u)[offset:offset + limit]]


@router.get('/changes/{id}')
def detail(id: str, u: User = Depends(user), s: Session = Depends(db)):
    row = next((r for r in all_changes(s, u) if r['id'] == id), None)
    if not row: raise HTTPException(404, 'Change not found.')
    return row


class DrawingSetup(Mutation):
    part: str = Field(min_length=2, max_length=100)
    customer: str = Field(default='', max_length=160)


@router.post('/changes/{id}/drawing-workspace')
def setup_drawing(id: str, body: DrawingSetup, u: User = Depends(user), s: Session = Depends(db)):
    require(u, 'ENGINEER', 'MANAGER')
    parent = get_change(s, u, id)
    # Idempotent repeat opens the existing workspace without creating duplicate projects.
    if parent.data.get('drawing_project_id'):
        return detail(id, u, s)
    parent = get_change(s, u, id, True, body.expected_version)
    mutable(parent)
    if parent.domain != 'engineering' or parent.classification != 'INTERNAL':
        raise HTTPException(422, 'Drawing workspaces require an internal engineering change.')
    if parent.data.get('approvals') or any(a.get('status') == 'COMPLETE' for a in parent.data.get('actions', [])):
        raise HTTPException(409, 'Reviewed changes require a successor; existing decisions cannot be replaced.')
    snapshot(s, u.tenant, parent.id, 'BEFORE_DRAWING_WORKSPACE', view(parent))
    project = add(s, u, 'project', {'name': parent.data['title'], 'part': body.part,
        'customer': body.customer, 'nodes': [], 'edges': [], 'graph_verified': False,
        **{k:parent.data.get(k) for k in ['effectivity','effective_date','effectivity_reference']},
        'demo': parent.data.get('demo', False), 'controlled_change_id': parent.id})
    patch(parent, drawing_project_id=project.id)
    details = {'project_id': project.id, 'reason': body.reason,
               'authority': 'Drawing verification and engineering/quality release workflow',
               'previous_evidence': 'Retained in the original aggregate and immutable snapshot; not transferred as verified drawing evidence.'}
    event(s, u, parent, 'DRAWING_WORKSPACE_OPENED', details)
    audit(s, u, project.id, 'PROJECT_CREATED', {'controlled_change_id': parent.id, 'part': body.part})
    s.commit()
    return detail(id, u, s)
