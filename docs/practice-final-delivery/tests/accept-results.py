"""Accept completed source-bound coverage after a documented harness-only retry.

Never relabel the initial failed plan. All original ancillary results and both
fresh 21-case trainer reruns must pass on the exact frozen production bytes.
"""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--initial',type=Path,required=True);ap.add_argument('--retest',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
def read(root,name):return json.loads((root/name).read_text())
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def valid(r,n):return r.get('passed')is True and len(r.get('checks',[]))==n and all(c.get('passed')is True for c in r['checks'])
first=read(args.initial,'run-summary.json');retry=read(args.retest,'run-summary.json')
assert first['completePlanExecuted'] and first['sourceUnchanged'] and first['buildUnchanged']
assert {r['name']for r in first['runs']if not r['passed']}=={'chromium','webkit'}
assert retry['passed'] and retry['sourceUnchanged'] and retry['buildUnchanged']
assert retry['sourceLibrarySHA256']==first['sourceLibrarySHA256']
assert retry['productionSnapshot']==first['productionSnapshot']
current={str(p.relative_to(ROOT/'dist')):digest(p)for p in sorted((ROOT/'dist').rglob('*'))if p.is_file()}
assert current==first['productionSnapshot']
libfile=ROOT/'src/features/practice/assets/hand-poses.json';library=json.loads(libfile.read_text());assert digest(libfile)==first['sourceLibrarySHA256']
allowed=sorted(k for k,p in library['poses'].items()if p.get('audit',{}).get('collisionPassed')is True and p.get('audit',{}).get('contactPassed')is True)
trainers={e:read(args.retest,e+'/browser-trainer-'+e+'.json')for e in ['chromium','webkit']}
reg=read(args.initial,'regressions/regression-summary.json');camera=read(args.initial,'camera-controls/camera-controls.json');inspection=read(args.initial,'inspection-gates/inspection-gate-browser.json');reveal=read(args.initial,'hand-reveal/hand-reveal-browser.json')
records=[*trainers.values(),camera,inspection,reveal]
for r in records:
 if 'buildArtifactsUnchangedDuringRun'in r:assert r['buildArtifactsUnchangedDuringRun']
 assets=r.get('productionArtifactSHA256',{})
 # Camera supplement uses its own runtime evidence; all asset-bearing suites
 # must explicitly bind the exact frozen output and current library.
 if assets:
  assert all(current.get('assets/'+name)==sha for name,sha in assets.items())
  assert any(name.startswith('hand-poses-')and sha==first['sourceLibrarySHA256']for name,sha in assets.items())
assert camera.get('productionSceneSHA256') and all(current.get('assets/'+name)==sha for name,sha in camera['productionSceneSHA256'].items())
assert inspection['sourceInspectionAllowed']==allowed
checks={'chromium21':valid(trainers['chromium'],21),'webkit21':valid(trainers['webkit'],21),'originalRegressions107':reg.get('passed')is True and sum(r.get('checks',0)for r in reg.get('runs',[]))==107,'camera2':valid(camera,2),'inspectionGates2':valid(inspection,2),'reveal4':valid(reveal,4)}
assert inspection['sourceLibrarySHA256']==first['sourceLibrarySHA256']
checks['all42InspectionCases']=all(c.get('chordsChecked')==42 and c.get('sourceTransformsMatched')is True and c.get('allowed')==len(allowed) and c.get('blocked')==42-len(allowed) and len(c.get('views',[]))==6 for c in inspection['checks'])
errors={}
for name,r in [('chromium',trainers['chromium']),('webkit',trainers['webkit']),('inspection',inspection),('reveal',reveal),('camera',camera)]:
 errors[name]={key:len(r.get(key,[]))for key in ['consoleErrors','runtimeErrors','networkErrors','failedRequests','badResponses']}
checks['zeroUnexpectedErrors']=not any(v for value in errors.values()for v in value.values())
result={'passed':all(checks.values()),'checks':checks,'sourceLibrarySHA256':first['sourceLibrarySHA256'],'frozenProductionBytesMatched':True,'singleInitialRunPassed':False,'initialPreparationFailuresRetained':True,'initialReports':str(args.initial),'trainerRetestReports':str(args.retest),'retryReason':retry['reason'],'browserTrainers':{e:{'passed':valid(r,21),'cases':len(r['checks']),'passedCases':sum(c['passed']is True for c in r['checks']),'browserVersion':r['browserVersion']}for e,r in trainers.items()},'originalRegressions':107,'sourceInspectionAllowed':allowed,'inspectionCases':{'engines':2,'chordsPerEngine':42,'allowedPerEngine':len(allowed),'blockedPerEngine':42-len(allowed),'correctedCameraCaptures':12},'errors':errors,'physicalIPadSafariTested':False,'anatomicalHandsApprovedByHarness':0,'limitations':['An opacity reveal is not a certified physical chord-change path.','Linux WebKit and Chromium software graphics do not establish physical iPad Safari or GPU performance.','These tests validate rendering/behavior; anatomy and collision acceptance remain separate.']}
args.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));raise SystemExit(not result['passed'])
