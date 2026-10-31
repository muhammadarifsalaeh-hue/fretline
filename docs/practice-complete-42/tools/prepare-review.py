"""Collect independently audited candidates without changing any runtime pose.
Best numerical candidates remain research assets until multiview review.
"""
import copy,hashlib,importlib.util,json,subprocess
import numpy as np
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];LOCAL=ROOT/'.local-preview/practice-complete-42';OUT=ROOT/'docs/practice-complete-42'
s=importlib.util.spec_from_file_location('measure',Path(__file__).with_name('measure-pose.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
meter=m.Measurements();base=copy.deepcopy(meter.context['library']);candidates={k:[]for k in base['poses']}
baseline=ROOT/'docs/practice-fingering-polish/tests/geometry/summary.json'
for row in json.loads(baseline.read_text())['rows']:
 p=base['poses'][row['id']];candidates[row['id']].append({'id':row['id'],'pose':p,'row':row,'source':'baseline:1f2836b','audit':str(baseline.relative_to(ROOT)),'support':meter.measure(p)})
for report_file in sorted(LOCAL.rglob('audit/summary.json')):
 proposal=report_file.parents[1]/'proposal-library.json'
 if not proposal.exists():continue
 report=json.loads(report_file.read_text());lib=json.loads(proposal.read_text())
 for row in report['rows']:
  key=row['id'];pose=lib['poses'][key]
  assert report['assetSha256']==base['assetSha256'];assert row['poseTransformSha256']==m.f.gate.transform_hash(pose)
  assert report['sourceChordSha256']==meter.context['chord_sha']
  support=meter.measure(pose)if row['geometricPassed']else None
  candidates[key].append({'id':key,'pose':pose,'row':row,'source':str(proposal.relative_to(ROOT)),'audit':str(report_file.relative_to(ROOT)),'support':support})
def rank(v):
 row=v['row'];support=v['support']or{};pose=v['pose'];chord=meter.context['chords'][v['id']];offsets=pose.get('pressOffsetsMm');wanted={f"{t['string']}:{t['fret']}"for t in m.f.effective_contacts(chord)}
 compatible='pressOffsetsMm'not in pose or isinstance(offsets,dict)and set(offsets)==wanted and all(type(value)in(int,float)and np.isfinite(value)and 1.5<=value<=min(24,m.f.m.fret_x(int(key.split(':')[1]))-m.f.m.fret_x(int(key.split(':')[1])-1)-5)for key,value in offsets.items())
 if not compatible:return(False,False,False,-1,-999999,-999999)
 return(row['geometricPassed']and support.get('thumbSupportPassed')and support.get('jointPlausibilityPassed'),row['geometricPassed'],row['skinAndClothSelfCrossingPairs']==0,sum(c['passed']for c in row.get('contacts',[]))/max(1,len(row.get('contacts',[]))),-(row['guitar'].get('crossingPairs')or 0),-row['skinAndClothSelfCrossingPairs'])
review=copy.deepcopy(base);rows=[]
for key,options in candidates.items():
 best=max(options,key=rank);review['poses'][key]=best['pose'];row={k:v for k,v in best.items()if k!='pose'};row['attemptsAudited']=len(options)-1;row['safeGeometryAndSupport']=bool(rank(best)[0]);row['visualReviewPassed']=False;row['teachingApproved']=False;rows.append(row)
(LOCAL/'review-library.json').write_text(m.f.previous.frozen_json(review));(OUT/'tests/candidate-inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'geometryPassed':sum(r['row']['geometricPassed']for r in rows),'geometryAndSupportPassed':sum(r['safeGeometryAndSupport']for r in rows),'auditedCandidates':sum(r['attemptsAudited']for r in rows),'notVisualOrTeachingApproval':True}));print('Missing new attempts:',[r['id']for r in rows if not r['attemptsAudited']and not r['row']['geometricPassed']])
