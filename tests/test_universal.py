import io
import json
from datetime import date
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from backend.main import app,LOGIN_ATTEMPTS
from backend.change_engine import table_items,StructuredDataDiff,analyze,AdjacencyGraph,read_table

P='/api/v1'
REASON='Reviewed against controlled fictional evidence'

def make(c,domain='supplier',classification='INTERNAL'):
    me=c.get(P+'/auth/me').json()
    r=c.post(P+'/changes',json={'domain':domain,'title':'Fictional controlled change','owner':me['id'],'reason':REASON,'classification':classification})
    assert r.status_code==201,r.text
    return r.json()

def mutate(c,change,path,body=None,method='POST',expected=200):
    response=c.request(method,P+'/changes/'+change['id']+path,json={'expected_version':change['version'],'reason':REASON,**(body or {})})
    assert response.status_code==expected,response.text
    return response.json()

def prepared(c,domain='supplier',classification='INTERNAL'):
    change=make(c,domain,classification)
    row={'id':'source','lead_time_days':7} if domain=='supplier' else {'id':'source','inspection_every_units':100} if domain=='quality' else {'id':'source','upper_tolerance':.1,'lower_tolerance':-.1}
    new={**row,('lead_time_days' if domain=='supplier' else 'inspection_every_units' if domain=='quality' else 'upper_tolerance'):(14 if domain=='supplier' else 20 if domain=='quality' else .02)}
    for side,values in [('old',row),('new',new)]:change=mutate(c,change,'/sources/'+side,{'label':side,'rows':[values]},'PUT')
    change=mutate(c,change,'/compare')
    return change

def ready(c,change):
    for side in ['old','new']:change=mutate(c,change,'/sources/'+side+'/verify')
    for d in change['analysis']['deltas']:change=mutate(c,change,'/deltas/'+d['id']+'/review',{'decision':'CONFIRMED'})
    change=mutate(c,change,'/graph/verify')
    for a in list(change['actions']):change=mutate(c,change,'/actions/'+a['id'],{'status':'COMPLETE','evidence':'Fictional controlled evidence reviewed, missing mappings independently resolved.'},'PATCH')
    assert change['blockers']==[]
    return change

def account(c,role):
    email=uuid4().hex+'@example.test';password='TestPassword!2026'
    r=c.post(P+'/users',json={'name':'Independent '+role,'email':email,'password':password,'role':role})
    assert r.status_code==201,r.text
    return {'id':r.json()['id'],'email':email,'password':password}

def sign(c,a):
    LOGIN_ATTEMPTS.clear();assert c.post(P+'/auth/login',json={'email':a['email'],'password':a['password']}).status_code==200

@pytest.mark.parametrize('domain,roles',[('engineering',['ENGINEER','QUALITY']),('quality',['QUALITY','ENGINEER']),('supplier',['PURCHASE','QUALITY','PLANNER'])])
def test_three_domain_lifecycle(company,domain,roles):
    c,admin=company;people=[account(c,role) for role in roles];change=prepared(c,domain)
    mutate(c,change,'/approve',{'action':'APPROVE'},expected=409)
    change=ready(c,change)
    assert change['status']=='READY_FOR_APPROVAL'
    for a in people:
        sign(c,a);change=mutate(c,change,'/approve',{'action':'APPROVE'})
    assert change['status']=='APPROVED'
    mutate(c,change,'/sources/new/correction',{'item_id':'source:lead_time_days','value':'15'},'PATCH',409)
    sign(c,admin);change=mutate(c,change,'/approve',{'action':'MAKE_EFFECTIVE'})
    assert change['status']=='EFFECTIVE'
    change=mutate(c,change,'/approve',{'action':'CLOSE'});assert change['status']=='CLOSED'
    for fmt in ['json','pdf','xlsx']:
        r=c.get(P+'/changes/'+change['id']+'/report?format='+fmt);assert r.status_code==200,r.text
        assert r.content.startswith({'json':b'{','pdf':b'%PDF','xlsx':b'PK'}[fmt])
    assert c.get(P+'/changes/'+change['id']+'/audit').json()
    assert c.get(P+'/audit?entity='+change['id']).json()==[]

def test_semantic_numeric_format_false_positive():
    a=table_items([{'id':'S','lead_time_days':'7.0','material':'  EN8  steel '}])
    b=table_items([{'id':'S','lead_time_days':7,'material':'EN8 steel'}])
    assert StructuredDataDiff().compare(a,b)==[]

def test_deterministic_leadtime_and_quality_metrics():
    a=analyze('supplier',table_items([{'id':'S','lead_time_days':7}]),table_items([{'id':'S','lead_time_days':14}]),[],[])
    assert a['deltas'][0]['metrics']['difference']=='7'
    assert a['deltas'][0]['metrics']['percent_change']=='100'
    assert a['contributors'][0]['rule_id']=='SUP-LEAD-001'
    b=analyze('quality',table_items([{'id':'C','inspection_every_units':100}]),table_items([{'id':'C','inspection_every_units':20}]),[],[])
    assert b['deltas'][0]['metrics']['interval_frequency_factor']=='5'
    assert b['business_exposure']['associated_order_value'] is None

@pytest.mark.parametrize('rows',[[{'id':'S','lead_time_days':'NaN'}],[{'id':'S','lead_time_days':-1}],[{'id':'S'},{'id':'S'}],[{'id':'S','inspection_every_units':0}],[{'id':'','lead_time_days':5}]])
def test_invalid_structured_values(rows):
    with pytest.raises(ValueError):table_items(rows)

def test_secure_parsers():
    for body,suffix in [(b'[{"id":"S","id":"T","lead_time_days":7}]','.json'),(b'[{"id":"S","lead_time_days":NaN}]','.json'),(b'id,id\nS,T','.csv'),(b'fake','.dwg')]:
        with pytest.raises(ValueError):read_table(body,suffix,'test'+suffix)
    from openpyxl import Workbook
    wb=Workbook();ws=wb.active;ws.append(['id','lead_time_days']);ws.append(['S','=7+7']);buf=io.BytesIO();wb.save(buf)
    with pytest.raises(ValueError,match='Formulas'):read_table(buf.getvalue(),'.xlsx','bad.xlsx')

def test_paths_cycles_depth_and_false_impact():
    nodes=[{'id':x,'type':'part'} for x in ['a','b','c','d','unrelated']]
    edges=[{'source':a,'target':b,'relation':'AFFECTS'} for a,b in [('a','b'),('a','c'),('b','d'),('c','d'),('d','a')]]
    result=AdjacencyGraph().traverse(nodes,edges,['a'],depth=6)
    assert {n['id'] for n in result['nodes']}=={'a','b','c','d'}
    assert len(result['paths']['d'])==2
    assert result['cycle_paths']
    assert AdjacencyGraph().traverse(nodes,edges,['a'],depth=1)['truncated']
    assert AdjacencyGraph().traverse(nodes,edges,['a'],limit=2)['truncated']

def test_corrections_preserve_original_and_invalidate(company):
    c,_=company;change=prepared(c);old_version=change['version']
    change=mutate(c,change,'/sources/new/correction',{'item_id':'source:lead_time_days','value':'15'},'PATCH')
    assert change['analysis'] is None
    assert change['sources']['new']['items'][0]['original_value']=='14'
    assert change['sources']['new']['items'][0]['value']=='15'
    r=c.post(P+'/changes/'+change['id']+'/compare',json={'expected_version':old_version,'reason':REASON});assert r.status_code==409

def test_same_person_cannot_approve_twice(company):
    c,_=company;change=ready(c,prepared(c))
    change=mutate(c,change,'/approve',{'action':'APPROVE'})
    mutate(c,change,'/approve',{'action':'APPROVE'},expected=409)

def test_commercial_acl_all_surfaces_and_explicit_grant(company):
    c,admin=company;reader=account(c,'QUALITY');change=prepared(c,classification='COMMERCIAL')
    sign(c,reader)
    assert c.get(P+'/changes').json()==[]
    for path in ['', '/impact','/audit','/report','/sources/old/download']:
        assert c.get(P+'/changes/'+change['id']+path).status_code==404
    assert c.get(P+'/audit?entity='+change['id']).json()==[]
    sign(c,admin);mutate(c,change,'/access',{'user_id':reader['id'],'grant':True})
    sign(c,reader);assert c.get(P+'/changes/'+change['id']).status_code==200
    sign(c,admin);mutate(c,change,'/access',{'user_id':reader['id'],'grant':False})
    sign(c,reader);assert c.get(P+'/changes/'+change['id']).status_code==404

def test_tenant_isolation(company):
    c,_=company;change=prepared(c)
    with TestClient(app,headers={'X-ChangeGuard':'1'}) as other:
        a={'name':'Other','organization':'Other company','email':uuid4().hex+'@test.example','password':'TestPassword!2026'}
        assert other.post(P+'/auth/register',json=a).status_code==201;sign(other,a)
        for path in ['', '/impact','/audit','/report','/sources/new/download']:
            assert other.get(P+'/changes/'+change['id']+path).status_code==404
        assert other.get(P+'/changes').json()==[]

def test_viewer_and_sensitive_input_restrictions(company):
    c,admin=company;viewer=account(c,'VIEWER');change=make(c)
    mutate(c,change,'/sources/old',{'label':'A','rows':[{'id':'S','unit_price':50}]},'PUT',422)
    commercial=make(c,classification='COMMERCIAL')
    mutate(c,commercial,'/sources/old',{'label':'A','rows':[{'id':'S','employee_name':'Test'}]},'PUT',422)
    sign(c,viewer)
    mutate(c,change,'/compare',expected=403)

def test_graph_validation_and_rule_override_invalidation(company):
    c,_=company;change=prepared(c)
    nodes=[{'id':'source','label':'Supplier','type':'supplier','updated_at':date.today().isoformat()}]
    body={'nodes':nodes,'edges':[{'source':'source','target':'missing','relation':'AFFECTS','evidence':'Test mapping'}]}
    mutate(c,change,'/graph',body,'PUT',422)
    r=c.put(P+'/domain-settings',json={'expected_version':0,'rule_points':{'SUP-LEAD-001':45},'reason':REASON});assert r.status_code==200,r.text
    change=c.get(P+'/changes/'+change['id']).json();assert change['analysis'] is None
    change=mutate(c,change,'/compare');assert change['analysis']['contributors'][0]['points']==45

def test_source_integrity_and_upload(company):
    c,_=company;change=make(c)
    r=c.post(P+'/changes/'+change['id']+'/sources/old/upload',params={'label':'A','expected_version':change['version'],'reason':REASON},files={'file':('supplier.csv',b'id,lead_time_days\nS,7','text/csv')})
    assert r.status_code==200,r.text
    change=r.json();assert change['sources']['old']['items'][0]['source']['row']==2
    assert 'storage_key' not in r.text
    from backend.db import Session
    from backend.universal_models import ControlledChange
    from backend.main import STORAGE
    with Session() as s:
        record=s.get(ControlledChange,change['id']);(STORAGE/record.data['sources']['old']['storage_key']).write_bytes(b'tampered')
    assert c.get(P+'/changes/'+change['id']+'/sources/old/download').status_code==409

def test_report_queue_snapshot_and_acl(company):
    c,admin=company;reader=account(c,'VIEWER');change=prepared(c,classification='COMMERCIAL')
    result=c.post(P+'/changes/'+change['id']+'/report-jobs',json={'format':'json'})
    assert result.status_code==202,result.text
    job=result.json()['id']
    from backend.main import process_one
    assert process_one()
    assert c.get(P+'/reports/'+job).json()['status']=='SUCCEEDED'
    assert c.get(P+'/reports/'+job+'/download').json()['change']['id']==change['id']
    assert not any(j['id']==job for j in c.get(P+'/jobs').json())
    sign(c,reader)
    assert c.get(P+'/reports/'+job).status_code==404
    assert c.get(P+'/reports/'+job+'/download').status_code==404

def test_excel_relationship_preview_and_commit(company):
    c,_=company;change=prepared(c)
    template=c.get(P+'/imports/templates/relationships?format=xlsx')
    params={'expected_version':change['version'],'reason':REASON}
    path=P+'/imports/'+change['id']+'/dependencies'
    preview=c.post(path,params=params,files={'file':('map.xlsx',template.content)})
    assert preview.status_code==200,preview.text
    assert preview.json()['valid']
    assert c.get(P+'/changes/'+change['id']).json()['version']==change['version']
    saved=c.post(path,params={**params,'commit':True},files={'file':('map.xlsx',template.content)})
    assert saved.status_code==200,saved.text
    assert saved.json()['analysis'] is None
    assert len(saved.json()['edges'])==1

def test_tolerance_band_arithmetic():
    old=table_items([{'id':'C27','nominal':20,'unit':'mm','upper_tolerance':.1,'lower_tolerance':-.1}])
    new=table_items([{'id':'C27','nominal':20,'unit':'mm','upper_tolerance':.02,'lower_tolerance':-.02}])
    result=analyze('engineering',old,new,[],[])
    assert all(d['type']=='TOLERANCE_TIGHTENED' for d in result['deltas'])
    assert all(float(d['metrics']['band_reduction_percent'])==80 for d in result['deltas'])

def test_named_commercial_reviewer_can_own_cross_domain_action(company):
    c,admin=company;reviewer=account(c,'QUALITY');change=prepared(c,classification='COMMERCIAL')
    mutate(c,change,'/access',{'user_id':reviewer['id'],'grant':True})
    change=mutate(c,change,'/actions',{'title':'Review supplier quality evidence','owner':reviewer['id'],'department':'Quality','due_date':date.today().isoformat()})
    action=change['actions'][-1]
    sign(c,reviewer)
    change=mutate(c,change,'/actions/'+action['id'],{'status':'COMPLETE','evidence':'Fictional supplier approval evidence independently reviewed.'},'PATCH')
    assert change['actions'][-1]['status']=='COMPLETE'
