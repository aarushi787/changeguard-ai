from pathlib import Path
from uuid import uuid4
import io
import pytest
from fastapi.testclient import TestClient
from backend.main import app, process_one, LOGIN_ATTEMPTS

PREFIX='/api/v1'
def post(c,path,data):return c.post(PREFIX+path,json=data)

def prepare(c):
    p=post(c,'/projects',{'name':'Test assembly','part':'GS-204','customer':'Fictional customer'}).json()
    ids=[]
    for rev in ['A','B']:
        response=c.post(f'{PREFIX}/projects/{p["id"]}/revisions?revision={rev}',files={'file':(f'{rev}.csv',Path(f'samples/characteristics-{rev}.csv').read_bytes(),'text/csv')})
        assert response.status_code==202,response.text; ids.append(response.json()['revision']['id']); assert process_one()
    r=post(c,'/change-sets',{'project_id':p['id'],'old_revision_id':ids[0],'new_revision_id':ids[1],'title':'Tolerance tightening'})
    assert r.status_code==201,r.text
    return p,ids,r.json()

def satisfy(c,p,ids,cs):
    for r in c.get(f'{PREFIX}/projects/{p["id"]}/revisions').json():
        for ch in r['characteristics']:
            body={k:ch[k] for k in ['characteristic_id','label','type','nominal','upper_tolerance','lower_tolerance','unit','raw','critical','safety','source_page']}; body['reason']='Checked against controlled test source'
            assert c.put(f'{PREFIX}/revisions/{r["id"]}/characteristics/{ch["characteristic_id"]}',json=body).status_code==200
        assert post(c,f'/revisions/{r["id"]}/verify-completeness',{'reason':'All source characteristics reviewed'}).status_code==200
    assert c.put(f'{PREFIX}/projects/{p["id"]}/graph',json={'nodes':[{'id':'C27','label':'Bearing seat','type':'characteristic'},{'id':'cp','label':'Control Plan','type':'document'}],'edges':[{'source':'C27','target':'cp'}],'verified':True,'reason':'Reviewed full process map'}).status_code==200
    cs=post(c,f'/change-sets/{cs["id"]}/reanalyze',{'reason':'Recompute after evidence verification'}).json()
    for ch in cs['changes']:assert post(c,f'/change-sets/{cs["id"]}/changes/{ch["id"]}/review',{'decision':'ACCEPTED','reason':'Validated against controlled source'}).status_code==200
    for d in cs['documents']:assert c.patch(f'{PREFIX}/change-sets/{cs["id"]}/documents/{d["id"]}',json={'status':'REVIEWED','owner':'Test engineer','due_date':'2026-09-10','reason':'Controlled content reviewed and updated'}).status_code==200
    for a in cs['actions']:assert c.patch(f'{PREFIX}/change-sets/{cs["id"]}/actions/{a["id"]}',json={'status':'COMPLETE','reason':'Capability evidence verified for test scenario'}).status_code==200
    assert c.get(f'{PREFIX}/change-sets/{cs["id"]}/release-gates').json()['blockers']==[]

def test_auth_and_csrf(client):
    assert client.get(PREFIX+'/projects').status_code==401
    r=client.post(PREFIX+'/auth/login',headers={'X-ChangeGuard':''},json={'email':'a','password':'b'})
    assert r.status_code==403
    r=client.post(PREFIX+'/auth/login',headers={'Origin':'https://evil.example'},json={'email':'a','password':'b'})
    assert r.status_code==403

def test_end_to_end_release_and_exports(company):
    c,account=company;p,ids,cs=prepare(c)
    path=f'/change-sets/{cs["id"]}/transition'
    assert post(c,path,{'action':'RELEASE','reason':'Attempt without approvals'}).status_code==409
    satisfy(c,p,ids,cs)
    assert post(c,path,{'action':'QUALITY_APPROVE','reason':'Cannot skip engineering stage'}).status_code==409
    assert post(c,path,{'action':'ENGINEERING_APPROVE','reason':'Engineering evidence verified'}).json()['status']=='QUALITY_REVIEW'
    assert post(c,path,{'action':'QUALITY_APPROVE','reason':'Same person cannot approve both'}).status_code==409
    email=f'{uuid4().hex}@example.test'
    assert post(c,'/users',{'name':'Quality Reviewer','email':email,'password':'TestPassword!2026','role':'QUALITY'}).status_code==201
    with TestClient(app,headers={'X-ChangeGuard':'1'}) as quality:
        LOGIN_ATTEMPTS.clear(); assert post(quality,'/auth/login',{'email':email,'password':'TestPassword!2026'}).status_code==200
        assert post(quality,path,{'action':'QUALITY_APPROVE','reason':'Quality evidence independently reviewed'}).json()['status']=='APPROVED'
        assert post(quality,path,{'action':'RELEASE','reason':'Quality cannot release'}).status_code==403
    assert post(c,path,{'action':'RELEASE','reason':'Authorized manager releases verified revision'}).json()['status']=='RELEASED'
    assert post(c,f'/change-sets/{cs["id"]}/reanalyze',{'reason':'Cannot rewrite released evidence'}).status_code==409
    assert post(c,f'/revisions/{ids[0]}/verify-completeness',{'reason':'Cannot mutate released source'}).status_code==409
    for fmt in ['pdf','xlsx']:
        report=c.get(f'{PREFIX}/change-sets/{cs["id"]}/report?format={fmt}')
        assert report.status_code==200,report.text
        assert report.content.startswith(b'%PDF' if fmt=='pdf' else b'PK')
    trail=c.get(PREFIX+'/audit?entity='+cs['id']).json()
    assert any(e['operation']=='RELEASE' for e in trail)

def test_tenant_isolation_every_resource(company):
    c,account=company;p,ids,cs=prepare(c)
    with TestClient(app,headers={'X-ChangeGuard':'1'}) as other:
        email=f'{uuid4().hex}@example.test'; LOGIN_ATTEMPTS.clear()
        assert post(other,'/auth/register',{'name':'Other tenant','organization':'Another Company','email':email,'password':'TestPassword!2026'}).status_code==201
        post(other,'/auth/login',{'email':email,'password':'TestPassword!2026'})
        for path in [f'/projects/{p["id"]}',f'/projects/{p["id"]}/revisions',f'/change-sets/{cs["id"]}',f'/change-sets/{cs["id"]}/report',f'/revisions/{ids[0]}/download-token',f'/revisions/{ids[0]}/pages/1']:
            assert other.get(PREFIX+path).status_code==404,path
        assert other.get(PREFIX+'/change-sets').json()==[]
        assert other.get(PREFIX+'/audit?entity='+cs['id']).json()==[]
        assert post(other,f'/change-sets/{cs["id"]}/transition',{'action':'RELEASE','reason':'Cross-tenant release denied'}).status_code==404

def test_viewer_cannot_mutate(company):
    c,account=company; email=f'{uuid4().hex}@example.test'
    post(c,'/users',{'name':'Read only','email':email,'password':'TestPassword!2026','role':'VIEWER'})
    LOGIN_ATTEMPTS.clear(); post(c,'/auth/login',{'email':email,'password':'TestPassword!2026'})
    assert post(c,'/projects',{'name':'Forbidden','part':'Test'}).status_code==403
    assert post(c,'/users',{'name':'Escalation','email':'bad@example.test','password':'TestPassword!2026','role':'ADMIN'}).status_code==403

def test_approval_invalidated_by_source_edit(company):
    c,_=company;p,ids,cs=prepare(c);satisfy(c,p,ids,cs)
    assert post(c,f'/change-sets/{cs["id"]}/transition',{'action':'ENGINEERING_APPROVE','reason':'Evidence is reviewed'}).status_code==200
    revision=c.get(f'{PREFIX}/projects/{p["id"]}/revisions').json()[0];ch=revision['characteristics'][0]
    body={k:ch[k] for k in ['characteristic_id','label','type','nominal','upper_tolerance','lower_tolerance','unit','raw','critical','safety','source_page']};body.update(nominal=21,reason='Correct measurement against source')
    assert c.put(f'{PREFIX}/revisions/{revision["id"]}/characteristics/{ch["characteristic_id"]}',json=body).status_code==200
    refreshed=c.get(f'{PREFIX}/change-sets/{cs["id"]}').json()
    assert refreshed['approvals']==[] and refreshed['stale'] and refreshed['status']=='AI_ANALYSIS_COMPLETE'

def test_upload_security_duplicate_and_path(company):
    c,_=company;p,ids,cs=prepare(c)
    assert c.post(f'{PREFIX}/projects/{p["id"]}/revisions?revision=X',files={'file':('../../evil.pdf',b'not a pdf','application/pdf')}).status_code==422
    assert c.post(f'{PREFIX}/projects/{p["id"]}/revisions?revision=X',files={'file':('drawing.step',b'ISO-10303-21','application/octet-stream')}).status_code==422
    assert c.post(f'{PREFIX}/projects/{p["id"]}/revisions?revision=A',files={'file':('A.csv',b'test','text/csv')}).status_code==409
    assert c.post(f'{PREFIX}/projects/{p["id"]}/revisions?revision=Z',headers={'Content-Length':str(22*1024*1024)},content=b'').status_code==413

def test_download_tokens_auth_and_scope(company):
    c,_=company;p,ids,cs=prepare(c)
    url=c.get(f'{PREFIX}/revisions/{ids[0]}/download-token').json()['url']
    assert c.get(url).status_code==200
    assert c.get(url.replace(ids[0],ids[1])).status_code==403
    assert c.get(f'{PREFIX}/revisions/{ids[0]}/file?token=bad').status_code==403
    post(c,'/auth/logout',{})
    assert c.get(url).status_code==401

def test_job_failure_recorded(company):
    c,_=company;p=post(c,'/projects',{'name':'Bad CSV fixture','part':'P-1'}).json()
    r=c.post(f'{PREFIX}/projects/{p["id"]}/revisions?revision=A',files={'file':('A.csv',b'characteristic_id,nominal\nC1,NaN','text/csv')})
    assert r.status_code==202;process_one()
    jobs=c.get(PREFIX+'/jobs').json();assert jobs[0]['status']=='FAILED' and jobs[0]['failure_reason']

def test_inventory_and_rag_tenant_provenance(company):
    c,_=company;p,ids,cs=prepare(c)
    r=c.post(f'{PREFIX}/projects/{p["id"]}/inventory',files={'file':('inventory.csv',Path('samples/inventory.csv').read_bytes(),'text/csv')}); assert r.status_code==201
    assert c.get(f'{PREFIX}/change-sets/{cs["id"]}').json()['stale']
    r=c.post(PREFIX+'/knowledge',files={'file':('fixture.pdf',Path('samples/GS-204-Rev-C.pdf').read_bytes(),'application/pdf')});assert r.status_code==202
    hits=c.get(PREFIX+'/knowledge/search?q=Material').json();assert hits['results'] and hits['results'][0]['sha256'] and hits['results'][0]['source_location']

def test_formula_injection_export():
    from backend.reports import workbook_bytes
    from openpyxl import load_workbook
    wb=load_workbook(io.BytesIO(workbook_bytes({'Test':[['Title'],['=HYPERLINK("evil")']]})))
    assert wb.active['A2'].data_type=='s' and wb.active['A2'].value.startswith("'")

def test_audit_orm_immutable(company):
    from backend.db import Session,Audit
    from sqlalchemy import select
    with Session() as s:
        row=s.scalar(select(Audit)); row.operation='tampered'
        with pytest.raises(ValueError):s.commit()

def test_migration_append_only_database():
    import os,subprocess,tempfile
    from sqlalchemy import create_engine,text
    name=str(Path('tmp',f'migration-{uuid4().hex}.db').resolve()).replace('\\','/')
    env={**os.environ,'DATABASE_URL':'sqlite:///'+name}
    result=subprocess.run(['python','-m','alembic','upgrade','head'],env=env,capture_output=True,text=True)
    assert result.returncode==0,result.stderr
    engine=create_engine(env['DATABASE_URL'])
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO audit_events (id,tenant,actor,entity,operation,details,created) VALUES ('1','t','u','e','test','{}',CURRENT_TIMESTAMP)"))
    with pytest.raises(Exception):
        with engine.begin() as conn:conn.execute(text("DELETE FROM audit_events"))
    engine.dispose()
