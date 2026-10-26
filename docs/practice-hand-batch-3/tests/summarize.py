"""Summarize only Batch3's frozen build reports, preserving actual failures."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--reports',type=Path,required=True);args=ap.parse_args();folder=args.reports

def load(path):return json.loads((folder/path).read_text())
def errors(report):return {k:len(report.get(k,[])) for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses','networkErrors']}
trainer={e:load(e+'/browser-trainer-'+e+'.json') for e in ['chromium','webkit']}
regression=load('regressions/regression-summary.json');camera=load('camera-controls/camera-controls.json');batch=load('batch-poses/batch-poses-browser.json');reveal=load('hand-reveal/hand-reveal-browser.json')
source=ROOT/'src/features/practice/assets/hand-poses.json';library=json.loads(source.read_text());source_sha=hashlib.sha256(source.read_bytes()).hexdigest()
artifacts=trainer['chromium']['productionArtifactSHA256']
matching=artifacts==trainer['webkit']['productionArtifactSHA256']==batch['productionArtifactSHA256']
matching=matching and all(artifacts.get(name)==sha for name,sha in reveal['productionArtifactSHA256'].items())
matching_source=source_sha==batch['poseLibrarySHA256'] and any(n.startswith('hand-poses-') and sha==source_sha for n,sha in artifacts.items())
gates=['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed']
approved=[k for k,p in library['poses'].items() if p.get('status')=='verified' and p.get('reviewed') is True and all(p.get('audit',{}).get(g) is True for g in gates)]
report={'scope':'Frozen-production browser/render/lifecycle evidence; not anatomical or physical iPad approval',
 'productionArtifactSHA256':artifacts,'matchingProductionAssetsAcrossReports':matching,'matchingCurrentPoseLibrary':matching_source,
 'browserTrainer':{e:{'passed':r['passed'],'cases':len(r['checks']),'passedCases':sum(x['passed'] for x in r['checks']),'failedCases':[x['case'] for x in r['checks'] if not x['passed']],'browserVersion':r['browserVersion'],'errors':errors(r),'performance':next(x['details'] for x in r['checks'] if x['case']=='performance-lifecycle'),'buildArtifactsUnchangedDuringRun':r['buildArtifactsUnchangedDuringRun']} for e,r in trainer.items()},
 'legacyBrowserRegressions':{'passed':regression['passed'],'checks':sum(r['checks'] for r in regression['runs']),'runs':regression['runs']},
 'cameraControls':{'passed':camera['passed'],'cases':len(camera['checks']),'errors':errors(camera)},
 'newCandidateRendering':{'passed':batch['passed'],'chords':batch['chords'],'engineViewportCases':len(batch['checks']),'errors':errors(batch),'actualSourceTransformsChecked':list(dict.fromkeys(['C']+batch['chords'])),'fourViews':['angle','side','back','player']},
 'handReveal':{'passed':reveal['passed'],'engineMotionCases':len(reveal['checks']),'errors':errors(reveal),'controlledClockCaptures':True,'physicalBoneInterpolation':False},
 'verifiedTeachingHands':approved,'handsApprovedByThisHarness':0,
 'limitations':['Linux WebKit and Chromium software rendering are not physical iPad Safari or native iPad performance evidence.','These browser checks do not certify skin/finger collisions or anatomical accuracy.','The opacity reveal changes no bone transforms; a physical cross-chord trajectory remains unverified.','Historical Phase5–9 static failures are reported separately.']}
report['expectedCaseCoverage']=all(len(r['checks'])==21 for r in trainer.values()) and sum(r['checks'] for r in regression['runs'])==107 and len(camera['checks'])==2 and len(batch['checks'])==4 and len(reveal['checks'])==4
report['passed']=report['expectedCaseCoverage'] and matching and matching_source and all(r['passed'] for r in trainer.values()) and regression['passed'] and camera['passed'] and batch['passed'] and reveal['passed']
(folder/'final-summary.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='productionArtifactSHA256'},ensure_ascii=False,indent=2))
raise SystemExit(0 if report['passed'] else 1)
