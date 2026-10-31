"""Negative tests for evidence/geometry eligibility, not synthesized pose approval."""
import copy,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v4.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
s=importlib.util.spec_from_file_location('selector',Path(__file__).with_name('select-eligible.py'));selector=importlib.util.module_from_spec(s);s.loader.exec_module(selector)
context=f.load_context();base=context['library'];source=json.loads((ROOT/'.local-preview/practice-complete-42/robust-open/A7/result.json').read_text());original=json.loads((ROOT/source['proposalFile']).read_text());report=json.loads((ROOT/source['auditReport']).read_text());rows=[]
def digest(v):return hashlib.sha256(f.previous.frozen_json(v).encode()).hexdigest()
def select(lib,r):return selector.select(f,base,lib,r,digest(lib),context['model_sha'],context['chord_sha'],['A7'])
def check(name,mutate,expect_pass=False):
 lib=copy.deepcopy(original);r=copy.deepcopy(report);mutate(lib,r)
 try:chosen,decisions=select(lib,r);passed=decisions[0]['selected']
 except (AssertionError,ValueError,KeyError,TypeError):passed=False
 assert passed==expect_pass,name;rows.append({'name':name,'passed':True});print('PASS',name,flush=True)
check('Real independent audit can select only geometry, never teaching approval',lambda p,r:None,True)
check('Wrong applied bone/root cannot reuse a prior mesh report',lambda p,r:p['poses']['A7']['root']['positionMm'].__setitem__(0,p['poses']['A7']['root']['positionMm'][0]+1))
check('A stale pressure map cannot reuse a prior mesh report',lambda p,r:p['poses']['A7']['pressOffsetsMm'].__setitem__(next(iter(p['poses']['A7']['pressOffsetsMm'])),12))
check('Missing required owner contact cannot pass',lambda p,r:r['rows'][0]['contacts'].pop())
check('Wrong finger cannot pass a claimed positive report',lambda p,r:r['rows'][0]['contacts'][0].__setitem__('finger',4))
check('Wrong string cannot pass a claimed positive report',lambda p,r:r['rows'][0]['contacts'][0].__setitem__('string',6))
check('Wrong fret cannot pass a claimed positive report',lambda p,r:r['rows'][0]['contacts'][0].__setitem__('fret',3))
check('A penetrating owner surface cannot pass',lambda p,r:r['rows'][0]['contacts'][0].__setitem__('actualOwnerPalmarSkinClearanceMm',-.1))
check('A distant owner surface cannot pass',lambda p,r:r['rows'][0]['contacts'][0].__setitem__('actualOwnerPalmarSkinClearanceMm',1))
check('Missing one physical string cannot pass',lambda p,r:r['rows'][0]['strings'].pop())
check('Blocked open string cannot pass',lambda p,r:next(s for s in r['rows'][0]['strings']if s['fret']==0).__setitem__('wholeSkinClearanceMm',.1))
check('Self-crossing cannot pass',lambda p,r:r['rows'][0].__setitem__('skinAndClothSelfCrossingPairs',1))
check('False is not an integer zero collision count',lambda p,r:r['rows'][0].__setitem__('skinAndClothSelfCrossingPairs',False))
check('Guitar intersection cannot pass',lambda p,r:r['rows'][0]['guitar'].__setitem__('crossingPairs',1))
check('False cannot masquerade as zero guitar intersections',lambda p,r:r['rows'][0]['guitar'].__setitem__('crossingPairs',False))
check('Wood penetration cannot pass',lambda p,r:r['rows'][0].__setitem__('maximumWoodDepthMm',.1))
check('Non-finite wood measurements cannot pass',lambda p,r:r['rows'][0].__setitem__('maximumWoodDepthMm',float('nan')))
check('Unexpected barre span cannot pass',lambda p,r:r['rows'][0]['barreCoverage'].append({'finger':1,'string':5,'fret':1,'passed':True,'palmarClearanceMm':0,'effectiveFinger':3,'effectiveFret':2}))
def rebinding(p,r):
 r['librarySnapshotSha256']=digest(p);r['rows'][0]['poseTransformSha256']=f.gate.transform_hash(p['poses']['A7']);r['rows'][0]['pressureSHA256']=hashlib.sha256(json.dumps(p['poses']['A7'].get('pressOffsetsMm'),sort_keys=True,separators=(',',':')).encode()).hexdigest()
def bad_pressure(p,r):p['poses']['A7']['pressOffsetsMm']['6:12']=9;rebinding(p,r)
check('Even re-labelled metadata cannot approve a noncanonical pressure key',bad_pressure)
def bad_quat(p,r):p['poses']['A7']['root']['quaternion']=[0,0,0,0];rebinding(p,r)
check('Even re-labelled metadata cannot approve an invalid root quaternion',bad_quat)
def fake_approval(p,r):p['poses']['A7'].update(status='verified',reviewed=True);p['poses']['A7']['audit'].update(anatomyPassed=True,multiViewReviewed=True);rebinding(p,r)
lib=copy.deepcopy(original);r=copy.deepcopy(report);fake_approval(lib,r);chosen,decisions=select(lib,r);assert decisions[0]['selected']and chosen['poses']['A7']['status']=='needs-review'and chosen['poses']['A7']['reviewed']is False and chosen['poses']['A7']['audit']['anatomyPassed']is False;rows.append({'name':'Automatic geometry cannot manufacture a human/anatomical certification','passed':True})
(ROOT/'docs/practice-complete-42/tests/selection-negative.json').write_text(json.dumps({'passed':True,'checks':len(rows),'rows':rows},indent=2)+'\n');print(len(rows),'passed')
