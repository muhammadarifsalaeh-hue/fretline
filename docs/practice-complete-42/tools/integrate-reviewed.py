"""Import only actual-render-reviewed, exact-mesh-audited real hand poses.
Independent anatomy/teaching gates remain false; rejected poses stay hidden.
"""
import copy,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-complete-42';LOCAL=ROOT/'.local-preview/practice-complete-42'
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v5.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
s=importlib.util.spec_from_file_location('selector',Path(__file__).with_name('select-eligible.py'));selector=importlib.util.module_from_spec(s);s.loader.exec_module(selector)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
context=f.load_context();base=copy.deepcopy(context['library']);review_lib=json.loads((LOCAL/'review-library.json').read_text());visual=json.loads((OUT/'tests/visual-review.json').read_text());inventory={r['id']:r for r in json.loads((OUT/'tests/candidate-inventory.json').read_text())};result=copy.deepcopy(base);rows=[]
direction=json.loads((OUT/'tests/pressure-direction/summary.json').read_text())
assert direction['librarySHA256']==sha(LOCAL/'review-library.json') and direction['modelSHA256']==context['model_sha']
directions={r['id']:r for r in direction['rows']}
for checked in visual['rows']:
 key=checked['id']
 if not checked['technicalVisualPassed']:continue
 p=review_lib['poses'][key];scene=hashlib.sha256(json.dumps({'root':p['root'],'bones':p['bones'],'pressure':p.get('pressOffsetsMm')},sort_keys=True,separators=(',',':')).encode()).hexdigest();assert scene==checked['sceneSHA256'],'Re-capture/review a changed candidate before import';record=inventory[key];assert record['safeGeometryAndSupport']and record['row']['geometricPassed']and record['support']['jointPlausibilityPassed']and record['support']['thumbSupportPassed']
 assert directions[key]['poseTransformSHA256']==f.gate.transform_hash(p) and directions[key]['contactDirectionPassed'],'Pressure must come from the owned palmar surface above each string'
 for view in checked['views']:assert sha(ROOT/view['file'])==view['imageSHA256']and view['sceneSHA256']==scene
 if record['source']=='baseline:1f2836b':assert p==base['poses'][key]
 else:
  proposal=ROOT/record['source'];report=json.loads((ROOT/record['audit']).read_text());lib=json.loads(proposal.read_text())
  if report['rows'][0].get('contactSemantics'):selected,decisions=selector.select(f,base,lib,report,sha(proposal),context['model_sha'],context['chord_sha'],[key])
  else:selected,decisions=f.previous.select_audited_replacements(base,lib,report,sha(proposal),context['model_sha'],context['chord_sha'],[key])
  assert decisions[0]['selected'];p=selected['poses'][key]
 p=copy.deepcopy(p);p['status']='needs-review';p['reviewed']=False;p['audit']={'collisionPassed':True,'contactPassed':True,'anatomyPassed':False,'multiViewReviewed':False};p['technicalReview']={'actualFourViewRendersInspected':True,'sceneSHA256':scene,'evidence':'docs/practice-complete-42/tests/visual-review.json','independentInstructorApproval':False};result['poses'][key]=p;rows.append({'id':key,'geometryReport':record['audit'],'sceneSHA256':scene,'thumbSupport':record['support'],'technicalVisualPassed':True,'teachingApproved':False})
for key in context['accepted']:
 assert result['poses'][key]['root']==base['poses'][key]['root']
 for name,bone in base['poses'][key]['bones'].items():
  if key not in ['B7','Gmaj7','Dsus2']or not name.startswith('finger1-'):assert result['poses'][key]['bones'][name]==bone
 assert result['poses'][key].get('pressOffsetsMm')==base['poses'][key].get('pressOffsetsMm')
file=ROOT/'src/features/practice/assets/hand-poses.json';backup=LOCAL/'runtime-before-reviewed-import.json'
if not backup.exists():backup.write_bytes(file.read_bytes())
assert sha(backup)==context['library_sha'];tmp=file.with_suffix('.next.json');tmp.write_text(f.previous.frozen_json(result));tmp.replace(file);report={'baselineSHA256':context['library_sha'],'runtimeLibrarySHA256':sha(file),'count':42,'technicalDisplayHands':len(rows),'newDisplayHands':len({r['id']for r in rows}-context['accepted']),'notCompleteAll42':len(rows)!=42,'independentTeachingApprovals':0,'rows':rows};(OUT/'tests/import-reviewed.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
