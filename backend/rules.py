"""Explainable versioned manufacturing rules; no inferred capability values."""
import json
from pathlib import Path

def assess(change,affected,inventory,pack):
    config=json.loads((Path(__file__).parent.parent/'rules/core.json').read_text())
    c=change.get('new') or change['old'];contributors=[];recommendations=[]
    flags={'tightened':change['type']=='TIGHTENED','material':change['type']=='MATERIAL_CHANGE','gdt':change['type']=='GDT_CHANGE','uncertain':change['type'] in {'UNKNOWN','REMOVED'},'critical':any(v and v.get('critical') for v in [change.get('old'),change.get('new')]),'safety':any(v and v.get('safety') for v in [change.get('old'),change.get('new')]),'inventory':bool(inventory),'supplier':any(n['type']=='supplier' for n in affected),'low_confidence':change['confidence']<.8}
    if not any(flags[k] for k in ['tightened','material','gdt','uncertain']):flags['other']=True
    for rule in config['rules']:
        if not flags.get(rule['when']):continue
        points=rule['points']
        if rule['when']=='tightened' and (change.get('tightening_factor') or 999)<pack['risk']['tightening_high']:points=30
        why=rule['why']
        if rule['when']=='tightened' and change.get('metrics',{}).get('band_reduction_percent') is not None:why=f"Tolerance band reduced by {change['metrics']['band_reduction_percent']:g}%. "+why
        contributors.append({'rule_id':rule['id'],'points':points,'reason':why})
        for domain in rule['reviews']:
            recommendations.append({'rule_id':rule['id'],'rule_version':config['version'],'engine':'RULE_BASED','title':f'Review {domain}','domain':domain,'why':why,'source':{'characteristic_id':change['characteristic_id'],**c.get('source_location',{})},'confidence':change['confidence'],'mandatory':True})
    raw=sum(c['points'] for c in contributors);score=min(100,raw);t=pack['risk'];level='CRITICAL' if score>=t['critical_score'] else 'HIGH' if score>=t['high_score'] else 'MEDIUM' if score>=t['medium_score'] else 'LOW'
    return {'score':score,'uncapped_score':raw,'cap':100,'level':level,'contributors':contributors,'rule_version':config['version'],'engine':'RULE_BASED','recommendations':recommendations,'reasons':[c['reason'] for c in contributors],'confidence':change['confidence'],'required_verification':['Machine capability verification required.','Confirm source extraction and dependency mapping completeness.'],'affected_entities':affected}
