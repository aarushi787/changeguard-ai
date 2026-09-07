import asyncio
import copy
import io
from pathlib import Path
import pytest
from backend.intelligence import characteristic,compare,assess,load_pack,DeterministicProvider
from backend.comparison import comparison_model
from backend.evidence import enrich,place_balloons
from backend.drawing import parse_line
from backend.boundary import BodyLimit
from test_api import prepare,post,PREFIX

def test_band_arithmetic_and_rule_evidence():
    a=characteristic('C27','Seat',20,.1,-.1);b={**a,'upper_tolerance':.02,'lower_tolerance':-.02,'critical':True}
    c=compare([a],[b])[0]
    assert c['type']=='TIGHTENED' and c['metrics']['band_reduction_percent']==80
    assert c['metrics']['old_tolerance_band']==.2 and c['metrics']['new_tolerance_band']==.04
    risk=assess(c,[],[],load_pack('precision_engineering'))
    assert risk['score']==min(100,sum(r['points'] for r in risk['contributors']))
    assert any(r['rule_id']=='CG-TOL-004' and r['source']['characteristic_id']=='C27' for r in risk['recommendations'])

def test_removing_critical_flag_preserves_risk_contributor():
    a={**characteristic('C27','Seat',20,.1,-.1),'critical':True};b={**a,'critical':False}
    risk=assess(compare([a],[b])[0],[],[],load_pack('precision_engineering'))
    assert any(r['rule_id']=='CG-CTQ-001' for r in risk['contributors'])

def test_verification_cannot_invent_source_box(company):
    c,_=company;p,ids,cs=prepare(c)
    rev=c.get(f'{PREFIX}/projects/{p["id"]}/revisions').json()[0];ch=rev['characteristics'][0]
    body={k:ch[k] for k in ['characteristic_id','label','type','nominal','upper_tolerance','lower_tolerance','unit','raw','critical','safety','source_page']}
    body.update(bbox=[100,100,20,10],reason='Invalid source coordinates must fail')
    assert c.put(f'{PREFIX}/revisions/{rev["id"]}/characteristics/{ch["characteristic_id"]}',json=body).status_code==422

def test_stale_workbench_decision_rejected(company):
    c,_=company;p,ids,cs=prepare(c)
    rev=c.get(f'{PREFIX}/projects/{p["id"]}/revisions').json()[0]
    path=f'/revisions/{rev["id"]}/characteristics/C27/decision'
    body={'decision':'VERIFIED','reason':'Fictional source checked for regression','expected_version':rev['version']}
    assert post(c,path,body).status_code==200
    assert post(c,path,{**body,'decision':'REJECTED'}).status_code==409

@pytest.mark.parametrize('field,value',[('quantity',4),('critical',True),('safety',True),('raw','20 ±0.1 THROUGH')])
def test_equal_numbers_do_not_hide_requirements(field,value):
    a=characteristic('C1','Hole',20,.1,-.1,raw='20 ±0.1');b={**a,field:value}
    assert compare([a],[b])

def test_formatting_and_move_are_non_engineering():
    a=characteristic('C1','Seat',20,.1,-.1,raw='20.00 +/- 0.10')
    b={**a,'raw':'20 ± 0.1','source_location':{'page':2,'bbox':[10,20,30,40]}}
    assert compare([a],[b])==[] and comparison_model([a],[b])[0]['type']=='MOVED'

def test_unique_relocation_and_ambiguity():
    a=characteristic('P1L1','Bearing seat',20,.1,-.1)
    b={**a,'characteristic_id':'P2L10','upper_tolerance':.02,'lower_tolerance':-.02}
    assert compare([a],[b])[0]['matching_method']=='UNIQUE_LABEL_TYPE_REVIEW_REQUIRED'
    assert len(compare([a,{**a,'characteristic_id':'P1L2'}],[b]))==3

@pytest.mark.parametrize('text,kind',[('C1: Seat: Ø20 +0.1/-0.02 mm','diameter'),('C2: Radius: R5 ±0.1 mm','radius'),('C3: Angle: 45 ±1 deg','angle'),('C4: M10 x 1.5-6H','thread'),('Ra 1.6 um','surface_finish'),('DATUM A MMC','gdt')])
def test_extended_parser(text,kind):
    c=parse_line(text,1,[1,2,3,4],1)
    assert c['type']==kind and c['verification_status']=='REVIEW_REQUIRED'

def test_quantity_and_duplicate_pdf_identifiers():
    c=parse_line('C3: Holes: 4 x Ø10 ±0.1 mm',1,[1,2,3,4],1)
    assert c['quantity']==4
    import fitz
    d=fitz.open()
    for _ in range(2):
        p=d.new_page();p.insert_text((30,30),'C1: Seat: 20 +/- 0.1 mm')
    r=DeterministicProvider().extract(d.tobytes(),'.pdf')
    assert len(r['characteristics'])==2 and len({c['characteristic_id'] for c in r['characteristics']})==2
    assert r['characteristics'][1]['confidence']<=.5

def test_balloon_numbers_survive_reorder_and_manual_position():
    a=characteristic('C27','Seat',20,.1,-.1,bbox=[50,50,100,65]);b=characteristic('C4','Hole',10,.1,-.1)
    chars=enrich([a,b]);assert chars[0]['balloon_number']==27
    moved=place_balloons(list(reversed(chars)),[{'page':1,'width':200,'height':200}]);assert {c['characteristic_id']:c['balloon_number'] for c in moved}=={'C27':27,'C4':4}

def test_actual_chunked_body_limit():
    called=[];sent=[];messages=[{'type':'http.request','body':b'1234','more_body':True},{'type':'http.request','body':b'5678','more_body':False}]
    async def app(scope,receive,send):called.append(True)
    async def receive():return messages.pop(0)
    async def send(m):sent.append(m)
    asyncio.run(BodyLimit(app,limit=6)({'type':'http','method':'POST'},receive,send))
    assert not called and sent[0]['status']==413

def test_verification_original_evidence_and_number_collision(company):
    c,_=company;p,ids,cs=prepare(c)
    rev=c.get(f'{PREFIX}/projects/{p["id"]}/revisions').json()[0];ch=rev['characteristics'][0]
    path=f'/revisions/{rev["id"]}/characteristics/{ch["characteristic_id"]}'
    r=post(c,path+'/decision',{'decision':'REJECTED','reason':'False extraction checked against source'})
    assert r.status_code==200 and r.json()['characteristics'][0]['extracted_original']==ch['extracted_original']
    assert post(c,path+'/decision',{'decision':'VERIFIED','reason':'Rechecked source confirms characteristic'}).status_code==200
    r=c.patch(PREFIX+path+'/annotation',json={'balloon_number':27,'reason':'Stable characteristic mapping retained'})
    assert r.status_code==200
    assert c.get(f'{PREFIX}/change-sets/{cs["id"]}').json()['stale'] is True
    report=c.get(f'{PREFIX}/change-sets/{cs["id"]}/report?format=json')
    assert report.status_code==200 and report.json()['report']['changes'][0]['metrics']['band_reduction_percent']==80

def test_source_integrity_blocks_reports(company):
    from backend.db import Session,Record
    from backend.main import STORAGE
    c,_=company;p,ids,cs=prepare(c)
    with Session() as s:r=s.get(Record,ids[0]);path=STORAGE/r.data['storage_key']
    path.write_bytes(b'changed outside controlled storage')
    assert c.get(f'{PREFIX}/change-sets/{cs["id"]}/report').status_code==409

def test_merge_split_retains_originals(company):
    c,_=company;p,ids,cs=prepare(c)
    rev=c.get(f'{PREFIX}/projects/{p["id"]}/revisions').json()[0];ch=rev['characteristics'][0]
    fields=['characteristic_id','label','type','nominal','upper_tolerance','lower_tolerance','unit','raw','critical','safety','source_page']
    replacement={k:ch[k] for k in fields};replacement.update(characteristic_id='C27_S1',reason='Split requires separately controlled review')
    response=post(c,f'/revisions/{rev["id"]}/reconcile',{'source_ids':['C27'],'replacements':[replacement,{**replacement,'characteristic_id':'C27_S2'}],'reason':'Split two separately controlled requirements'})
    assert response.status_code==200,response.text
    chars=response.json()['characteristics'];original=next(x for x in chars if x['characteristic_id']=='C27')
    assert original['verification_status']=='SUPERSEDED' and original['extracted_original']==ch['extracted_original']
    assert len({x['balloon_number'] for x in chars})==len(chars)
    assert post(c,f'/revisions/{rev["id"]}/verify-completeness',{'reason':'Premature completeness declaration'}).status_code==409

def test_async_report_snapshot_and_download(company):
    from backend.main import process_one
    c,_=company;p,ids,cs=prepare(c)
    job=post(c,f'/change-sets/{cs["id"]}/report-jobs',{'format':'json','kind':'impact'})
    assert job.status_code==202
    jid=job.json()['id'];assert c.get(PREFIX+f'/jobs/{jid}/report-download').status_code==409
    assert process_one()
    status=c.get(PREFIX+f'/jobs/{jid}').json()
    assert status['status']=='SUCCEEDED' and 'payload' not in status and 'events' not in status
    result=c.get(PREFIX+f'/jobs/{jid}/report-download');assert result.status_code==200
    assert result.json()['report']['changes'][0]['metrics']['band_reduction_percent']==80

def test_dependency_import_preview_and_commit(company):
    c,_=company;p,ids,cs=prepare(c)
    template=c.get(PREFIX+'/templates/process');assert template.status_code==200
    path=PREFIX+f'/projects/{p["id"]}/dependency-import'
    preview=c.post(path,files={'file':('process.xlsx',template.content)})
    assert preview.status_code==200 and preview.json()['mode']=='PREVIEW'
    assert c.get(PREFIX+f'/projects/{p["id"]}').json()['nodes']==[]
    commit=c.post(path+'?commit=true',files={'file':('process.xlsx',template.content)})
    assert commit.status_code==200 and commit.json()['edges'][0]['evidence']['row']==2
    assert c.get(PREFIX+f'/change-sets/{cs["id"]}').json()['stale']

def test_optimistic_update_rejects_stale_writer(company):
    from backend.db import Session,Record
    from sqlalchemy.orm.exc import StaleDataError
    c,_=company;p,_,_=prepare(c)
    with Session() as one,Session() as two:
        a=one.get(Record,p['id']);b=two.get(Record,p['id'])
        a.data={**a.data,'name':'First controlled edit'};one.commit()
        b.data={**b.data,'name':'Stale overwrite'}
        with pytest.raises(StaleDataError):two.commit()

def test_migration_snapshot_is_append_only():
    import tempfile
    tmp_path=Path(tempfile.mkdtemp(prefix="cg-migration-",dir="tmp")).resolve()
    import os,subprocess,sys
    from sqlalchemy import create_engine,text
    path=tmp_path/'migrated.db';url='sqlite:///'+str(path).replace('\\','/')
    env={**os.environ,'DATABASE_URL':url}
    subprocess.run([sys.executable,'-m','alembic','upgrade','head'],env=env,check=True,capture_output=True)
    engine=create_engine(url)
    with engine.begin() as connection:
        connection.execute(text("INSERT INTO evidence_snapshots (id,tenant,entity,stage,digest,data,created) VALUES ('a','t','e','TEST','abc','{}','2026-09-06')"))
    for query in ["UPDATE evidence_snapshots SET stage='CHANGED' WHERE id='a'","DELETE FROM evidence_snapshots WHERE id='a'"]:
        with pytest.raises(Exception,match='append-only'):
            with engine.begin() as connection:connection.execute(text(query))
    engine.dispose()
