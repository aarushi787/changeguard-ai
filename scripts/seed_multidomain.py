"""Idempotent fictional PRAGATI demo; never invoked automatically in production."""
import csv
import io
import json
import os
from datetime import date
from pathlib import Path
from sqlalchemy import select
from backend.main import app
from backend.db import Base,engine,Session,Organization,User,uid
from backend.security import hash_password
from backend.universal import create,NewChange,store_source,update_graph,GraphInput,compare_change,Mutation,patch
from backend.universal_models import ControlledChange
from backend.change_engine import read_table

def scenarios():
    today=date.today().isoformat()
    def node(id,label,type,**attrs):return {'id':id,'label':label,'type':type,'updated_at':today,'attributes':attrs}
    def edge(source,target):return {'source':source,'target':target,'relation':'AFFECTS','evidence':'Fictional demonstration mapping, not a validated production relationship.'}
    supplier_nodes=[node('SUP-17','Sahyadri Steel · supplier','supplier')]+[node('MAT-'+str(i),'Material '+str(i),'material') for i in range(1,5)]+[node('PRD-'+str(i),'Assembly '+str(i),'product') for i in range(1,4)]+[node('PO-'+str(i),'Open order '+str(i),'order') for i in range(1,6)]+[node('CUS-1','Aster Machinery','customer'),node('CUS-2','Deccan Drives','customer'),node('CP-204','CP-204 · incoming inspection','document'),node('OP-10','OP10 · material preparation','operation'),node('OP-30','OP30 · turning','operation')]
    supplier_edges=[edge('SUP-17','MAT-'+str(i)) for i in range(1,5)]+[edge('MAT-'+str(i),'PRD-'+str((i-1)%3+1)) for i in range(1,5)]+[edge('PRD-'+str((i-1)%3+1),'PO-'+str(i)) for i in range(1,6)]+[edge('PO-'+str(i),'CUS-'+str((i-1)%2+1)) for i in range(1,6)]+[edge('MAT-1','CP-204'),edge('MAT-2','OP-10'),edge('MAT-3','OP-30')]
    eng_nodes=[node('C27','Bearing diameter · GS-204','characteristic'),node('FEATURE','Bearing seat','feature'),node('OP30','OP30 · CNC turning','operation'),node('CNC04','CNC-04 · capability unknown','machine'),node('T08','Tool T08','tool'),node('CMM','CMM inspection','inspection'),node('CP021','Control Plan CP-021','document'),node('PF021','PFMEA PF-021','document'),node('WIP','147 WIP units · Rev C','inventory',quantity=147,unit='pieces',status='WIP'),node('FG','82 finished units · Rev C','inventory',quantity=82,unit='pieces',status='FINISHED')]
    eng_edges=[edge(a,b) for a,b in [('C27','FEATURE'),('FEATURE','OP30'),('OP30','CNC04'),('OP30','T08'),('C27','CMM'),('CMM','CP021'),('CMM','PF021'),('OP30','WIP'),('OP30','FG')]]
    qua_nodes=[node('CP-204','CP-204 · inspection interval','document'),node('IP204','Incoming inspection','inspection'),node('OP10','OP10 · inspection operation','operation'),node('GAUGE','Measuring equipment','machine'),node('WI204','WI-204 · operator instruction','document')]
    return [
        {'domain':'supplier','title':'Supplier lead time: 7 → 14 days','old':[{'id':'SUP-17','lead_time_days':7}],'new':[{'id':'SUP-17','lead_time_days':14}],'nodes':supplier_nodes,'edges':supplier_edges},
        {'domain':'engineering','title':'GS-204 bearing seat tolerance: Rev C → D','old':[{'id':'C27','nominal':20,'upper_tolerance':.1,'lower_tolerance':-.1,'unit':'mm'}],'new':[{'id':'C27','nominal':20,'upper_tolerance':.02,'lower_tolerance':-.02,'unit':'mm'}],'nodes':eng_nodes,'edges':eng_edges},
        {'domain':'quality','title':'Inspection frequency: 1 per 100 → 1 per 20','old':[{'id':'CP-204','inspection_every_units':100,'inspection_sample_count':1}],'new':[{'id':'CP-204','inspection_every_units':20,'inspection_sample_count':1}],'nodes':qua_nodes,'edges':[edge(a,b) for a,b in [('CP-204','IP204'),('IP204','OP10'),('IP204','GAUGE'),('OP10','WI204')]]}
    ]

def seed():
    if os.getenv('ENVIRONMENT')=='production' and os.getenv('ALLOW_DEMO_SEED')!='1':raise RuntimeError('Use a separate demonstration deployment.')
    Base.metadata.create_all(engine);root=Path('samples/multidomain');root.mkdir(parents=True,exist_ok=True)
    examples=scenarios()
    for ex in examples:
        for side in ['old','new']:
            stream=io.StringIO();writer=csv.DictWriter(stream,fieldnames=list(ex[side][0]));writer.writeheader();writer.writerows(ex[side]);(root/(ex['domain']+'-'+side+'.csv')).write_text(stream.getvalue(),encoding='utf-8')
        (root/(ex['domain']+'-dependencies.json')).write_text(json.dumps({'nodes':ex['nodes'],'edges':ex['edges']},indent=2),encoding='utf-8')
    (root/'README.txt').write_text('DEMONSTRATION DATA. Entirely fictional; CC0 synthetic software fixtures. Never use for manufacture or purchasing.\n',encoding='utf-8')
    with Session() as s:
        admin=s.scalar(select(User).where(User.email=='admin@pragati.changeguard.demo'))
        if admin:
            print('Pragati demo already exists; records preserved. Samples refreshed.');return
        org=Organization(id=uid(),name='PRAGATI INDUSTRIAL SYSTEMS',pack='precision_engineering');s.add(org)
        people={}
        for name,role in [('admin','ADMIN'),('engineering','ENGINEER'),('quality','QUALITY'),('purchase','PURCHASE'),('ppc','PLANNER'),('viewer','VIEWER')]:
            person=User(id=uid(),tenant=org.id,email=name+'@pragati.changeguard.demo',name=name.title()+' Reviewer',role=role,password=hash_password('ChangeGuard!2026'));s.add(person);people[name]=person
        s.commit();admin=people['admin']
        for ex in examples:
            created=create(NewChange(domain=ex['domain'],title=ex['title'],owner=admin.id,reason='Fictional demonstration of controlled industrial change',mode='CONNECTED'),admin,s)
            r=s.get(ControlledChange,created['id'])
            for side in ['old','new']:
                source=root/(ex['domain']+'-'+side+'.csv');content=source.read_bytes()
                store_source(s,admin,r,side,'Rev C' if side=='old' else 'Rev D',read_table(content,'.csv',source.name),'Fictional demonstration source',content,source.name)
            update_graph(r.id,GraphInput(expected_version=r.version,reason='Fictional dependency map for demonstration',nodes=ex['nodes'],edges=ex['edges']),False,admin,s)
            compare_change(r.id,Mutation(expected_version=r.version,reason='Demonstrate deterministic multi-domain analysis'),admin,s)
            patch(r,demo=True);s.commit()
        print('Created PRAGATI demonstration tenant with three unapproved controlled changes.')

if __name__=='__main__':seed()
