"""Generate report artifacts from fictional demo data and inspect every PDF page."""
import json
from pathlib import Path
from sqlalchemy import select
from backend.main import app
from backend.db import Session,User,Audit
from backend.universal_models import ControlledChange
from backend.universal import view
from backend.universal_reports import render

root=Path('output/pdf/multidomain');root.mkdir(parents=True,exist_ok=True)
with Session() as s:
    u=s.scalar(select(User).where(User.email=='admin@pragati.changeguard.demo'))
    results=[]
    for c in s.scalars(select(ControlledChange).where(ControlledChange.tenant==u.tenant)):
        events=[{'actor':e.actor,'operation':e.operation,'at':e.created.isoformat(),'details':e.details} for e in s.scalars(select(Audit).where(Audit.tenant==u.tenant,Audit.entity==c.id).order_by(Audit.created))]
        payload=view(c);payload['owner_name']=s.get(User,c.data['owner']).name
        for fmt in ['pdf','xlsx','json']:(root/(c.domain+'-impact.'+fmt)).write_bytes(render(payload,events,fmt))
        import fitz
        with fitz.open(root/(c.domain+'-impact.pdf')) as pdf:
            for i,page in enumerate(pdf):
                text=page.get_text()
                assert text.strip(),f'Empty report page {i}'
                assert 'Page '+str(i+1) in text,f'Missing footer {i}'
                if i in {0,1,2}:page.get_pixmap(matrix=fitz.Matrix(1,1)).save(root/(c.domain+'-page-'+str(i+1)+'.png'))
            results.append({'domain':c.domain,'pages':len(pdf),'formats':['pdf','xlsx','json']})
    (root/'verification.json').write_text(json.dumps(results,indent=2));print(json.dumps(results,indent=2))
