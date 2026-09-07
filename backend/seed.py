"""Explicit, idempotent fictional demonstration seed. Never runs automatically in production."""
import hashlib
import os
from pathlib import Path
from sqlalchemy import select
from backend.db import Base,engine,Session,Organization,User,Record,uid,Audit
from backend.security import hash_password
from backend.intelligence import DeterministicProvider

def seed():
    if os.getenv('ENVIRONMENT')=='production' and os.getenv('ALLOW_DEMO_SEED')!='1':
        raise RuntimeError('Demo seeding disabled in production. Use a separate evaluation deployment.')
    Base.metadata.create_all(engine)
    from backend.main import add, analysis, STORAGE
    with Session() as s:
        if s.scalar(select(User).where(User.email=='engineer@changeguard.demo')): return
        org=Organization(id=uid(),name='Northstar Precision Works',pack='precision_engineering'); s.add(org)
        people=[]
        for name,email,role in [('Arjun Mehta','engineer','ENGINEER'),('Maya Rao','quality','QUALITY'),('Elena Brooks','manager','ADMIN'),('Sam Patel','planner','PLANNER'),('Jordan Lee','viewer','VIEWER')]:
            u=User(id=uid(),tenant=org.id,name=name,email=email+'@changeguard.demo',role=role,password=hash_password('ChangeGuard!2026')); s.add(u); people.append(u)
        s.flush(); u=people[0]
        nodes=[{'id':'C27','label':'Bearing seat · C27','type':'characteristic'}, {'id':'feature','label':'Bearing seat Ø20','type':'feature'}, {'id':'op30','label':'OP30 · CNC turning','type':'operation'}, {'id':'cnc04','label':'CNC-04','type':'machine','capability':'UNKNOWN'}, {'id':'t08','label':'T08 · Finish insert','type':'tool'}, {'id':'fixture','label':'FX-12 · Soft jaws','type':'fixture'}, {'id':'inspection','label':'IP-204 · CMM inspection','type':'inspection'}, {'id':'cp021','label':'CP-021 · Control Plan','type':'document','owner':'Maya Rao'}, {'id':'pf021','label':'PF-021 · PFMEA','type':'document','owner':'Maya Rao'}, {'id':'wi030','label':'WI-030 · Work Instruction','type':'document','owner':'Arjun Mehta'}, {'id':'stock','label':'229 units · Rev C exposure','type':'inventory'}, {'id':'customer','label':'Aster Industrial Systems','type':'customer'}]
        edges=[{'source':a,'target':b} for a,b in [('C27','feature'),('feature','op30'),('op30','cnc04'),('op30','t08'),('op30','fixture'),('cnc04','inspection'),('inspection','cp021'),('inspection','pf021'),('op30','wi030'),('cp021','stock'),('stock','customer')]]
        p=add(s,u,'project',{'name':'Gear shaft assembly','part':'GS-204','customer':'Aster Industrial Systems','nodes':nodes,'edges':edges,'graph_verified':False,'demo':True})
        revs=[]
        for letter in ['C','D']:
            source=Path(f'samples/GS-204-Rev-{letter}.pdf'); content=source.read_bytes(); key=f'{uid()}.pdf'; (STORAGE/key).write_bytes(content)
            extraction=DeterministicProvider().extract(content,'.pdf')
            for c in extraction['characteristics']:
                if c['characteristic_id']=='C27': c['critical']=True
            r=add(s,u,'revision',{'project_id':p.id,'revision':letter,'filename':source.name,'storage_key':key,'suffix':'.pdf','sha256':hashlib.sha256(content).hexdigest(),'status':'READY','completeness_verified':False,**extraction}); revs.append(r)
        for status,qty,loc,batch in [('WIP',147,'Machining cell 04','B-260901'),('FINISHED',82,'Finished goods · A3','B-260829')]: add(s,u,'inventory',{'project_id':p.id,'part':'GS-204','revision':'C','status':status,'quantity':qty,'location':loc,'batch':batch,'production_order':'PO-2048','demo':True})
        changes,inventory,docs=analysis(s,u,revs[0],revs[1],p)
        cs=add(s,u,'change_set',{'project_id':p.id,'old_revision_id':revs[0].id,'new_revision_id':revs[1].id,'title':'Bearing seat tolerance refinement','number':'EC-0001','part':'GS-204','customer':p.data['customer'],'old_revision':'C','new_revision':'D','changes':changes,'inventory':inventory,'documents':docs,'actions':[{'id':uid(),'title':'Verify CNC-04 capability for the revised bearing seat tolerance','owner_id':u.id,'owner':u.name,'due_date':'2026-09-10','reason':'No machine capability record is available for ±0.02 mm.','status':'OPEN'},{'id':uid(),'title':'Review CMM inspection program IP-204 and measurement capability','owner_id':people[1].id,'owner':people[1].name,'due_date':'2026-09-11','reason':'Inspection method is linked to the tightened characteristic.','status':'OPEN'}],'approvals':[],'comments':[],'status':'ENGINEERING_REVIEW','stale':False,'demo':True})
        s.add(Audit(tenant=u.tenant,actor='system:demo-seed',entity=cs.id,operation='DEMONSTRATION_CREATED',details={'notice':'Entire dataset is fictional. No engineering validation has been performed.','source_revision':'C','target_revision':'D'})); s.commit()
        print('Demo ready: engineer@changeguard.demo / ChangeGuard!2026')

if __name__=='__main__': seed()
