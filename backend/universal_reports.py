"""Portable universal evidence report, with identical JSON/XLSX/PDF content sections."""
import io
import json
from datetime import datetime,timezone
from xml.sax.saxutils import escape
from backend.reports import workbook_bytes

def process_report(s,job,storage):
    import hashlib,time,logging
    from backend.db import uid,Audit
    start=time.monotonic()
    try:
        content=render(job.data['payload'],job.data['events'],job.data['format'])
        key=uid()+'.'+job.data['format'];(storage/key).write_bytes(content)
        job.data={**job.data,'status':'SUCCEEDED','storage_key':key,'sha256':hashlib.sha256(content).hexdigest(),'duration_ms':round((time.monotonic()-start)*1000)}
        s.add(Audit(tenant=job.tenant,actor='system:report',entity=job.data['change_id'],operation='REPORT_GENERATED',details={'scope':'universal','sha256':job.data['sha256'],'job_id':job.id}))
    except Exception as exc:
        job.data={**job.data,'status':'FAILED','failure_reason':'Report generation failed. Queue a new report; controlled evidence is unchanged.'}
        logging.getLogger('changeguard').error(json.dumps({'event':'universal_report_failed','job_id':job.id,'error_type':type(exc).__name__}))
    s.commit()

def render(change,events,format):
    generated=datetime.now(timezone.utc).isoformat();a=change.get('analysis') or {}
    payload={'generated_at':generated,'change':change,'audit':events,'notice':'Human decision support. No automatic operational changes.'}
    if format=='json':return json.dumps(payload,ensure_ascii=False,indent=2).encode()
    sheets={
        'Summary':[['Field','Value'],['Title',change['title']],['Domain',change['domain']],['Status',change['status']],['Generated UTC',generated],['Data','DEMONSTRATION DATA' if change.get('demo') else change['classification']],['Change ID',change['id']],['Owner',change.get('owner_name',change['owner'])],['Effectivity',change['effectivity']],['Effective date',change.get('effective_date')],['Source',change.get('sources',{}).get('old',{}).get('label')],['Target',change.get('sources',{}).get('new',{}).get('label')],['Exposure score',a.get('score')],['Severity',a.get('level')],['Business exposure',a.get('business_exposure')]],
        'Deltas':[['Object','Field','Old','New','Classification','Confidence','Decision','Reason','Source','Calculation']]+[[d.get(k) for k in ['object_id','field','old_value','new_value','type','confidence','decision','reason','source','metrics']] for d in a.get('deltas',[])],
        'Recommendations':[['Review','Why','Rule','Source','Confidence','Engine']]+[[r.get(k) for k in ['title','why','rule_id','source','confidence','engine']] for r in a.get('recommendations',[])],
        'Score contributors':[['Rule','Points','Reason','Engine']]+[[r.get(k) for k in ['rule_id','points','reason','engine']] for r in a.get('contributors',[])],
        'Dependencies':[['Source','Relation','Target','Evidence']]+[[r.get(k) for k in ['source','relation','target','evidence']] for r in change.get('edges',[])],
        'Actions':[['Title','Owner','Due','Status','Mandatory','Evidence']]+[[r.get(k) for k in ['title','owner','due_date','status','mandatory','evidence']] for r in change.get('actions',[])],
        'Approvals':[['Stage','User','Timestamp','Reason','Evidence digest']]+[[r.get(k) for k in ['stage','user','at','reason','digest']] for r in change.get('approvals',[])],
        'Unresolved':[['Blocker']]+[[b] for b in change.get('blockers',[])],
        'Audit':[['Actor','Event','Timestamp','Details']]+[[e.get(k) for k in ['actor','operation','at','details']] for e in events]
    }
    for side,source in change.get('sources',{}).items():
        sheets[side.title()+' evidence']=[['ID','Value','Original','Source','Engine','Verified']]+[[x['id'],x['value'],x['original_value'],x['source'],x['engine'],source['verified']] for x in source['items']]
    if format=='xlsx':return workbook_bytes(sheets)
    from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,PageBreak,KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet
    styles=getSampleStyleSheet();styles['BodyText'].fontSize=9;styles['BodyText'].leading=12
    stream=io.BytesIO();doc=SimpleDocTemplate(stream,pagesize=(595,842),leftMargin=42,rightMargin=42,topMargin=45,bottomMargin=45)
    story=[Paragraph('ChangeGuard AI',styles['Title']),Paragraph('Change & Impact Intelligence',styles['Heading2'])]
    for title,rows in sheets.items():
        if title!='Summary':story.append(PageBreak())
        story.append(Paragraph(escape(title),styles['Heading1']))
        if len(rows)==1:story.append(Paragraph('No records at report generation time.',styles['BodyText']))
        for index,row in enumerate(rows[1:],1):
            if title=='Summary':
                label,value=row
                if isinstance(value,(list,dict)):value=json.dumps(value,ensure_ascii=False)
                story.append(Paragraph('<b>'+escape(str(label))+'</b>: '+escape(str(value if value is not None else 'Not specified')),styles['BodyText']))
                story.append(Spacer(1,8));continue
            for key,value in zip(rows[0],row):
                if isinstance(value,(list,dict)):value=json.dumps(value,ensure_ascii=False)
                # Split lengthy audit JSON into bounded paragraphs so a large event cannot overflow a page.
                text=f'{key}: {value if value is not None else "UNKNOWN — DATA REQUIRED"}'
                for start in range(0,len(text),1800):story.append(Paragraph(escape(text[start:start+1800]),styles['BodyText']))
            story.append(Spacer(1,9))
    def footer(canvas,doc):
        canvas.setFont('Helvetica',8);canvas.drawString(42,25,'CONFIDENTIAL • '+('DEMONSTRATION DATA' if change.get('demo') else 'CONTROLLED EVIDENCE'));canvas.drawRightString(553,25,f'Page {doc.page}')
    doc.build(story,onFirstPage=footer,onLaterPages=footer);return stream.getvalue()
