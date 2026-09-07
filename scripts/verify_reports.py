"""Render the actual seeded report and ballooned drawing for local visual QA."""
from pathlib import Path
from sqlalchemy import select
import fitz
from backend.db import Session,Record,Audit,User
from backend.reports import make_report,balloon_export,drawing_previews
from backend.main import STORAGE,out,blockers

root=Path('output/pdf');root.mkdir(parents=True,exist_ok=True)
renders=Path('tmp/pdf-review');renders.mkdir(parents=True,exist_ok=True)
with Session() as s:
    cs=s.scalar(select(Record).where(Record.kind=='change_set'))
    if not cs:raise RuntimeError('Run the demo seed first.')
    events=[{'id':e.id,'created':e.created.isoformat(),'actor':e.actor,'operation':e.operation,'details':e.details} for e in s.scalars(select(Audit).where(Audit.entity==cs.id))]
    source=s.get(Record,cs.data['old_revision_id']); target=s.get(Record,cs.data['new_revision_id'])
    u=s.scalar(select(User).where(User.tenant==cs.tenant))
    payload={**out(cs),'source_sha256':source.data['sha256'],'target_sha256':target.data['sha256'],'unresolved':blockers(s,u,cs)}
    report=make_report(payload,events,'pdf','impact',drawing_previews([source.data,target.data],STORAGE));(root/'ChangeGuard-Demo-Impact.pdf').write_bytes(report)
    (root/'ChangeGuard-Demo-Impact.xlsx').write_bytes(make_report(payload,events,'xlsx','impact'))
    revision=s.get(Record,cs.data['new_revision_id'])
    balloon=balloon_export(revision.data,STORAGE,'pdf');(root/'GS-204-Rev-D-Ballooned.pdf').write_bytes(balloon)
for name in ['ChangeGuard-Demo-Impact','GS-204-Rev-D-Ballooned']:
    with fitz.open(root/f'{name}.pdf') as pdf:
        print(f'{name}: {len(pdf)} pages')
        for i,page in enumerate(pdf):
            page.get_pixmap(matrix=fitz.Matrix(1.25,1.25),alpha=False).save(renders/f'{name}-{i+1}.png')
            if not page.get_text().strip():raise RuntimeError('Empty report page')
