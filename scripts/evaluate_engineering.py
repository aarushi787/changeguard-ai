"""Reproducible synthetic challenge set. Results are not field-performance claims."""
import json
import time
from pathlib import Path
import fitz
from backend.intelligence import DeterministicProvider,characteristic,compare

root=Path('samples/evaluation');root.mkdir(parents=True,exist_ok=True)
provider=DeterministicProvider();cases=[]
for name,text,expected,rotation,scan in [
 ('symmetric','C27: Seat: 20 +/- 0.10 mm',(20,.1,-.1),0,False),
 ('asymmetric','C27: Seat: 20 +0.10/-0.02 mm',(20,.1,-.02),0,False),
 ('rotated','C27: Seat: 20 +/- 0.10 mm',(20,.1,-.1),90,False),
 ('missing_title','C27: Seat: 20 +/- 0.10 mm',(20,.1,-.1),0,False),
 ('small_text','C27: Seat: 20 +/- 0.10 mm',(20,.1,-.1),0,False),
 ('scanned','C27: Seat: 20 +/- 0.10 mm',(20,.1,-.1),0,True),
 ('low_resolution','C27: Seat: 20 +/- 0.10 mm',(20,.1,-.1),0,True),
 ('limit_only','C27: Seat limits 20.00 to 20.04 mm',(20,.04,0),0,False),
 ('bad_ocr_text','C27: Seat: 2O +/- O.1O mm',(20,.1,-.1),0,False),
 ('angle','C27: Angle: 45 +/- 1 deg',(45,1,-1),0,False),
]:
    d=fitz.open();p=d.new_page(width=500,height=300);p.insert_text((30,35),'DEMONSTRATION DATA - synthetic challenge',fontsize=10);p.insert_text((50,100),text,fontsize=6 if name=='small_text' else 12);p.set_rotation(rotation)
    if scan:
        pix=p.get_pixmap(matrix=fitz.Matrix(.6 if name=='low_resolution' else 2, .6 if name=='low_resolution' else 2));d.close();d=fitz.open();p=d.new_page(width=500,height=300);p.insert_image(p.rect,stream=pix.tobytes('png'))
    path=root/(name+'.pdf');path.write_bytes(d.tobytes());d.close();start=time.perf_counter();result=provider.extract(path.read_bytes(),'.pdf');duration=round((time.perf_counter()-start)*1000,2)
    predicted=[c for c in result['characteristics'] if c.get('nominal') is not None]
    correct=[c for c in predicted if (c['nominal'],c['upper_tolerance'],c['lower_tolerance'])==expected]
    cases.append({'case':name,'expected_numeric_characteristics':1,'predicted_numeric_characteristics':len(predicted),'correct_numeric_characteristics':len(correct),'passed':len(correct)==1 and len(predicted)==1,'duration_ms':duration,'warnings':result['warnings']})

base=characteristic('C27','Seat',20,.1,-.1,raw='20 +/- 0.10 mm');comparisons=[]
for name,new,expected in [('unchanged',base,None),('formatting',{**base,'raw':'20.00 ±0.100 mm'},None),('tightening',{**base,'upper_tolerance':.02,'lower_tolerance':-.02},'TIGHTENED'),('loosening',{**base,'upper_tolerance':.2,'lower_tolerance':-.2},'RELAXED'),('critical_flag',{**base,'critical':True},'PROCESS_CHANGE'),('added_qualifier',{**base,'raw':'20 +/- 0.10 mm THROUGH'},'MODIFIED')]:
    detected=compare([base],[new]);actual=detected[0]['type'] if detected else None;comparisons.append({'case':name,'expected':expected,'actual':actual,'passed':expected==actual})
tp=sum(c['correct_numeric_characteristics'] for c in cases);pred=sum(c['predicted_numeric_characteristics'] for c in cases);truth=len(cases)
result={'notice':'Synthetic author-created examples only. No claim of production drawing accuracy. Human correction rate requires a measured engineer study.','dataset_version':'cg-challenge-2','dimension_and_tolerance_precision':{'correct':tp,'predicted':pred,'ratio':tp/pred if pred else None},'dimension_and_tolerance_recall':{'correct':tp,'expected':truth,'ratio':tp/truth},'false_negative_characteristics':truth-tp,'false_positive_characteristics':pred-tp,'comparison_cases_passed':sum(c['passed'] for c in comparisons),'comparison_cases_total':len(comparisons),'human_correction_rate':'NOT_MEASURED','impact_rule_precision':'NOT_MEASURED_WITH_INDEPENDENT_ENGINEERS','cases':cases,'comparisons':comparisons}
out=Path('output/evaluation');out.mkdir(parents=True,exist_ok=True);(out/'results.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
lines=['# Synthetic engineering evaluation','',result['notice'],'',f'Numeric characteristic precision: {tp}/{pred}. Recall: {tp}/{truth}.',f'Comparison scenarios: {result["comparison_cases_passed"]}/{len(comparisons)} passed.','', '| Case | Exact numeric extraction | Duration ms |','|---|---|---|']+[f'| {c["case"]} | {"PASS" if c["passed"] else "MISSED — human review required"} | {c["duration_ms"]} |' for c in cases]
(out/'RESULTS.md').write_text('\n'.join(lines)+'\n',encoding='utf-8');print(json.dumps({k:v for k,v in result.items() if k not in {'cases','comparisons'}},indent=2))
