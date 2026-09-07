"""Cross-workflow integration invariants: one register, one release authority."""
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from backend.main import app, process_one
from tests.test_universal import make, prepared, mutate, account, sign, REASON, P


def setup(c, change, **extra):
    return c.post(P+'/workspace/changes/'+change['id']+'/drawing-workspace', json={
        'expected_version':change['version'],'part':'GS-204','reason':REASON,**extra})


def comparison(c, workspace):
    project=workspace['drawing']['project_id']; revisions=[]
    for label in ['A','B']:
        r=c.post(f'{P}/projects/{project}/revisions?revision={label}',
            files={'file':(label+'.csv',Path(f'samples/characteristics-{label}.csv').read_bytes(),'text/csv')})
        assert r.status_code==202,r.text
        revisions.append(r.json()['revision']['id']);assert process_one()
    body={'project_id':project,'title':'Controlled drawing integration',
          'old_revision_id':revisions[0],'new_revision_id':revisions[1]}
    r=c.post(P+'/change-sets',json=body);assert r.status_code==201,r.text
    return r.json(),body


def test_drawing_change_stays_in_one_register(company):
    c,_=company; parent=make(c,'engineering')
    r=setup(c,parent);assert r.status_code==200,r.text
    ws=r.json();assert ws['id']==parent['id'] and ws['workflow']=='DRAWING'
    assert ws['status']=='DRAFT' and ws['blockers']
    assert setup(c,parent).json()['drawing']==ws['drawing']
    drawing,body=comparison(c,ws)
    listing=c.get(P+'/workspace/changes').json()
    assert len(listing)==1 and listing[0]['id']==parent['id']
    assert listing[0]['drawing']['change_set_id']==drawing['id']
    assert listing[0]['actions'] and all(a['mandatory'] for a in listing[0]['actions'])
    assert c.post(P+'/change-sets',json=body).status_code==409
    assert mutate(c,parent,'/approve',{'action':'APPROVE'},expected=409)
    assert c.post(P+'/changes/'+parent['id']+'/report-jobs',json={'format':'pdf'}).status_code==409
    assert c.post(P+'/change-sets/'+drawing['id']+'/transition',json={'action':'RELEASE','reason':REASON}).status_code==409
    report=c.post(P+'/change-sets/'+drawing['id']+'/report-jobs',json={'format':'json','kind':'impact'})
    assert report.status_code==202,report.text
    assert process_one()
    result=c.get(P+'/jobs/'+report.json()['id']+'/report-download')
    assert result.status_code==200 and b'DRAWING_WORKSPACE_OPENED' in result.content


def test_conversion_retains_original_evidence_and_invalidates_parallel_writes(company):
    c,_=company;parent=prepared(c,'engineering');original=parent['sources']
    assert setup(c,parent).status_code==200
    old=c.get(P+'/changes/'+parent['id']).json()
    assert old['sources']==original
    events=c.get(P+'/changes/'+parent['id']+'/audit').json()
    assert any(e['operation']=='DRAWING_WORKSPACE_OPENED' for e in events)
    assert mutate(c,old,'/sources/new/correction',{'item_id':original['new']['items'][0]['id'],'value':'9'},'PATCH',409)
    assert c.get(P+'/workspace/changes/'+parent['id']).json()['analysis'] is None


def test_workspace_tenant_role_and_classification_boundaries(company):
    c,admin=company;parent=make(c,'engineering')
    viewer=account(c,'VIEWER');sign(c,viewer)
    assert setup(c,parent).status_code==403
    sign(c,admin)
    assert setup(c,make(c,'supplier')).status_code==422
    assert setup(c,make(c,'engineering','COMMERCIAL')).status_code==422
    assert setup(c,parent,expected_version=999).status_code==409
    assert setup(c,parent).status_code==200
    with TestClient(app,headers={'X-ChangeGuard':'1'}) as other:
        assert other.get(P+'/workspace/changes').status_code==401
        from uuid import uuid4
        email=uuid4().hex+'@example.test'
        assert other.post(P+'/auth/register',json={'email':email,'password':'TestPassword!2026','name':'Other Engineer','organization':'Other Tenant','pack':'precision_engineering'}).status_code==201
        sign(other,{'email':email,'password':'TestPassword!2026'})
        assert other.get(P+'/workspace/changes').json()==[]
        assert other.get(P+'/workspace/changes/'+parent['id']).status_code==404
        assert setup(other,parent).status_code==404


def test_legacy_drawings_and_structured_changes_share_register(company):
    c,_=company
    from tests.test_api import prepare
    _,_,legacy=prepare(c)
    structured=make(c,'quality')
    rows=c.get(P+'/workspace/changes').json()
    assert {r['id'] for r in rows}=={legacy['id'],structured['id']}
    assert next(r for r in rows if r['id']==legacy['id'])['workflow']=='DRAWING'
    assert next(r for r in rows if r['id']==structured['id'])['workflow']=='STRUCTURED'
    assert c.get(P+'/workspace/changes?limit=0').status_code==422


def test_reviewed_change_cannot_switch_authority(company):
    c,_=company
    from tests.test_universal import ready
    parent=ready(c,prepared(c,'engineering'))
    assert setup(c,parent).status_code==409


@pytest.mark.parametrize('future_date', [False, True])
def test_integrated_release_and_effective_date(company, future_date):
    from tests.test_api import satisfy
    c,admin=company
    parent=make(c,'engineering')
    if future_date:
        me=c.get(P+'/auth/me').json()
        parent=c.post(P+'/changes',json={'domain':'engineering','title':'Future dated drawing change',
            'owner':me['id'],'reason':REASON,'effectivity':'DATE','effective_date':'2099-01-01'}).json()
    ws=setup(c,parent).json();drawing,body=comparison(c,ws)
    project=c.get(P+'/projects/'+body['project_id']).json()
    satisfy(c,project,[body['old_revision_id'],body['new_revision_id']],drawing)
    path=P+'/change-sets/'+drawing['id']+'/transition'
    assert c.post(path,json={'action':'ENGINEERING_APPROVE','reason':REASON}).status_code==200
    assert c.post(path,json={'action':'QUALITY_APPROVE','reason':REASON}).status_code==409
    reviewer=account(c,'QUALITY');sign(c,reviewer)
    assert c.post(path,json={'action':'QUALITY_APPROVE','reason':REASON}).status_code==200
    sign(c,admin)
    response=c.post(path,json={'action':'RELEASE','reason':REASON})
    assert response.status_code==(409 if future_date else 200)
    if future_date:assert 'effective date' in response.text
    unified=c.get(P+'/workspace/changes/'+parent['id']).json()
    assert unified['status']==('APPROVED' if future_date else 'RELEASED') and len(unified['approvals'])==2
    assert unified['ready_for_approval'] is False
    assert mutate(c,parent,'/approve',{'action':'MAKE_EFFECTIVE'},expected=409)


def test_pdf_worker_stdout_is_only_json():
    import json, subprocess, sys
    r=subprocess.run([sys.executable,'-m','backend.extract_task','.pdf'],
        input=Path('samples/GS-204-Rev-C.pdf').read_bytes(),capture_output=True,check=True,timeout=120)
    payload=json.loads(r.stdout)
    assert payload['characteristics']
    assert any(c['characteristic_id']=='C27' for c in payload['characteristics'])
