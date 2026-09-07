"""Characteristic evidence, stable annotations and immutable snapshot utilities."""
import copy
import hashlib
import json
import re
from backend.db import EvidenceSnapshot

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
def snapshot(s,tenant,entity,stage,data):
    frozen=copy.deepcopy(data);row=EvidenceSnapshot(tenant=tenant,entity=entity,stage=stage,digest=digest(frozen),data=frozen)
    s.add(row);s.flush();return row
def active(chars):return [c for c in chars if c.get('verification_status') not in {'REJECTED','SUPERSEDED'}]
def confidence_band(c):return 'HIGH_CONFIDENCE' if c.get('confidence',0)>=.9 else 'REVIEW_REQUIRED' if c.get('confidence',0)>=.75 else 'LOW_CONFIDENCE'
def normalize(c):
    return {k:c.get(k) for k in ['type','nominal','upper_tolerance','lower_tolerance','unit','quantity','thread','surface_finish','gdt','raw']}
def enrich(chars):
    """Preserve issued numbers and raw extraction even if the review list changes."""
    items=copy.deepcopy(chars);used={c['balloon_number'] for c in items if c.get('balloon_number')}
    for c in items:
        c.setdefault('normalized',normalize(c));c['confidence_band']=confidence_band(c)
        c.setdefault('engine','HUMAN_CONFIRMED' if c.get('extraction_method','').startswith('human') else 'OCR' if 'ocr' in c.get('extraction_method','') else 'RULE_BASED')
        c.setdefault('extracted_original',{k:copy.deepcopy(v) for k,v in c.items() if k not in {'extracted_original','human_corrections'}})
        c.setdefault('human_corrections',[])
        if not c.get('balloon_number'):
            match=re.fullmatch(r'C(\d+)',c['characteristic_id']);number=int(match[1]) if match and int(match[1])>0 else 1
            while number in used:number+=1
            c['balloon_number']=number;used.add(number)
        c.setdefault('inspection_reference',f"INSP-{c['characteristic_id']}")
    return items

def place_balloons(chars,pages):
    items=enrich(chars);occupied={}
    for c in items:
        page=c.get('source_page',1);box=c.get('source_location',{}).get('bbox');p=next((p for p in pages if p['page']==page),{'width':842,'height':595})
        occupied.setdefault(page,[])
        if c.get('balloon_position'):
            pos=c['balloon_position'];occupied[page].append((pos['x'],pos['y']));continue
        if not box:continue
        x=max(13,min(p['width']-13,box[0]-19));y=max(13,min(p['height']-24,(box[1]+box[3])/2))
        candidates=[(x,y)]+[(x,min(p['height']-24,y+24*i)) for i in range(1,12)]+[(min(p['width']-13,x+28*i),y) for i in range(1,12)]
        def clear(cx,cy):
            return all((cx-a)**2+(cy-b)**2>=22**2 for a,b in occupied[page]) and not any(b[0]-10<cx<b[2]+10 and b[1]-10<cy<b[3]+10 for other in items if other['source_page']==page and (b:=other.get('source_location',{}).get('bbox')))
        choice=next((v for v in candidates if clear(*v)),None)
        c['balloon_position']={'x':(choice or (x,y))[0],'y':(choice or (x,y))[1],'page':page,'manual':False}
        c['balloon_collision']=choice is None;occupied[page].append(choice or (x,y))
    return items
