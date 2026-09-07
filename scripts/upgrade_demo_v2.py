"""Audited annotation/rule upgrade for unreleased fictional demo records only."""
from sqlalchemy import select
from backend.db import Session,Record,User
from backend.main import analysis,edit,audit,STORAGE
from backend.evidence import place_balloons,snapshot
from backend.graph import persist
import fitz

with Session() as s:
    u=s.scalar(select(User).where(User.email=='engineer@changeguard.demo'))
    if u:
        for p in s.scalars(select(Record).where(Record.tenant==u.tenant,Record.kind=='project')):
            sets=[r for r in s.scalars(select(Record).where(Record.tenant==u.tenant,Record.kind=='change_set')) if r.data['project_id']==p.id]
            if not p.data.get('demo') or any(r.data['status'] in {'RELEASED','APPROVED','QUALITY_REVIEW'} for r in sets):continue
            if p.data.get('evidence_version')==2:continue
            edges=persist(s,u.tenant,p.id,p.data['nodes'],p.data['edges'],'system:demo-upgrade')
            edit(p,edges=edges,evidence_version=2)
            for rev in s.scalars(select(Record).where(Record.tenant==u.tenant,Record.kind=='revision')):
                if rev.data['project_id']!=p.id:continue
                with fitz.open(STORAGE/rev.data['storage_key']) as doc:pages=[{'page':i+1,'width':v.cropbox.width,'height':v.cropbox.height,'unit':'pt','rotation':v.rotation} for i,v in enumerate(doc)]
                snapshot(s,u.tenant,rev.id,'LEGACY_EXTRACTION',rev.data)
                edit(rev,pages=pages,characteristics=place_balloons(rev.data['characteristics'],pages))
                audit(s,u,rev.id,'DEMO_EVIDENCE_UPGRADED',{'reason':'Preserved legacy extraction; added persistent annotation mapping and page geometry.'})
            for cs in sets:
                a=s.get(Record,cs.data['old_revision_id']);b=s.get(Record,cs.data['new_revision_id'])
                changes,inventory,docs=analysis(s,u,a,b,p)
                snapshot(s,u.tenant,cs.id,'LEGACY_ANALYSIS',cs.data)
                edit(cs,changes=changes,inventory=inventory,documents=docs,approvals=[],stale=False,status='ENGINEERING_REVIEW')
                audit(s,u,cs.id,'DEMO_RULES_UPGRADED',{'reason':'Fictional demo recomputed under CG-2.0 rules; human review remains required.'})
        s.commit()
print('Unreleased demonstration records upgraded where eligible.')
