"""Deterministic semantic comparisons, with formatting and movement separated from engineering."""
import re
from decimal import Decimal
from backend.evidence import active

FIELDS=['nominal','upper_tolerance','lower_tolerance','unit','label','type','quantity','thread','surface_finish','gdt','critical','safety']
def canonical_text(text):
    text=(text or '').replace('+/-','±').replace('ø','Ø').replace('⌀','Ø')
    text=re.sub(r'\d+(?:\.\d+)?',lambda m:format(Decimal(m[0]).normalize(),'f'),text)
    return re.sub(r'\s+','',text).casefold()

def comparison_model(old,new):
    a={c['characteristic_id']:c for c in active(old)};b={c['characteristic_id']:c for c in active(new)}
    pairs=[(cid,a[cid],b[cid],'STABLE_ID') for cid in sorted(a.keys()&b.keys())]
    remaining_a={k:v for k,v in a.items() if k not in b};remaining_b={k:v for k,v in b.items() if k not in a}
    # Match relocated parser-generated IDs only when a meaningful label/type is unique
    # on both sides. Explicit engineering IDs are never guessed or silently remapped.
    def key(c):return (canonical_text(c.get('label')),c.get('type'))
    for aid,x in list(remaining_a.items()):
        candidates=[(bid,y) for bid,y in remaining_b.items() if re.fullmatch(r'P\d+L\d+',bid) and key(x)==key(y)]
        if re.fullmatch(r'P\d+L\d+',aid) and key(x)[0] not in {'dimension','diameter',''} and len(candidates)==1 and sum(key(v)==key(x) for v in remaining_a.values())==1:
            bid,y=candidates[0];pairs.append((bid,x,y,'UNIQUE_LABEL_TYPE_REVIEW_REQUIRED'));del remaining_a[aid];del remaining_b[bid]
    pairs += [(cid,x,None,'UNMATCHED') for cid,x in remaining_a.items()]+[(cid,None,y,'UNMATCHED') for cid,y in remaining_b.items()]
    result=[]
    for cid,x,y,match in pairs:
        metrics={};kind='UNCHANGED'
        if not x:kind='ADDED'
        elif not y:kind='REMOVED'
        else:
            different=[k for k in FIELDS if x.get(k)!=y.get(k)]
            raw_changed=canonical_text(x.get('raw'))!=canonical_text(y.get('raw'))
            if different or raw_changed:
                kind='MODIFIED'
                if x.get('type')=='material':kind='MATERIAL_CHANGE'
                elif x.get('type') in {'note','standard'}:kind='SPECIFICATION_CHANGE'
                elif x.get('type')=='gdt' or x.get('gdt')!=y.get('gdt'):kind='GDT_CHANGE'
                elif x.get('unit')!=y.get('unit') or x.get('unit')=='UNKNOWN':kind='UNKNOWN'
                elif x.get('nominal') is not None and x.get('nominal')==y.get('nominal') and all(c.get(k) is not None for c in [x,y] for k in ['upper_tolerance','lower_tolerance']):
                    ow=Decimal(str(x['upper_tolerance']))-Decimal(str(x['lower_tolerance']));nw=Decimal(str(y['upper_tolerance']))-Decimal(str(y['lower_tolerance']))
                    metrics={'old_tolerance_band':float(ow),'new_tolerance_band':float(nw),'band_reduction_percent':float((ow-nw)/ow*100) if ow else None,'engine':'CALCULATED'}
                    if nw<ow and y['lower_tolerance']>=x['lower_tolerance'] and y['upper_tolerance']<=x['upper_tolerance']:kind='TIGHTENED'
                    elif nw>ow and y['lower_tolerance']<=x['lower_tolerance'] and y['upper_tolerance']>=x['upper_tolerance']:kind='RELAXED'
                    metrics['tightening_factor']=float(ow/nw) if kind=='TIGHTENED' and nw else None
                if kind=='MODIFIED' and any(k in different for k in ['critical','safety','quantity','thread']):kind='PROCESS_CHANGE'
                # A changed textual qualifier is not dismissed merely because numbers match.
            elif x.get('source_location')!=y.get('source_location'):kind='MOVED'
            elif x.get('raw')!=y.get('raw'):kind='VISUAL_ONLY'
        confidence=min(c.get('confidence',0) for c in [x,y] if c)
        if match=='UNIQUE_LABEL_TYPE_REVIEW_REQUIRED':confidence=min(confidence,.7)
        result.append({'id':cid,'characteristic_id':cid,'label':(y or x)['label'],'type':kind,'old':x,'new':y,'metrics':metrics,'tightening_factor':metrics.get('tightening_factor'),'confidence':confidence,'engine':'RULE_BASED','matching_method':match,'review':'PENDING','reason':''})
    return result

def compare(old,new):
    return [c for c in comparison_model(old,new) if c['type'] not in {'UNCHANGED','MOVED','VISUAL_ONLY'}]
