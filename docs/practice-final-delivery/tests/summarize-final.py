"""Summarize completed actual reports; skipped cases cannot become passes."""
from pathlib import Path
import argparse,hashlib,json
ROOT=Path(__file__).resolve().parents[3]
ap=argparse.ArgumentParser();ap.add_argument('--reports',type=Path,required=True);args=ap.parse_args();folder=args.reports
run=json.loads((folder/'run-summary.json').read_text())
def load(name):
 path=folder/name
 return json.loads(path.read_text())if path.is_file()else{}
def valid(report,count):return report.get('passed')is True and len(report.get('checks',[]))==count and all(c.get('passed')is True for c in report.get('checks',[]))
def errors(report):return {k:len(report.get(k,[]))for k in ['consoleErrors','runtimeErrors','failedRequests','badResponses','networkErrors']}
trainers={e:load(e+'/browser-trainer-'+e+'.json')for e in ['chromium','webkit']}
regression=load('regressions/regression-summary.json');camera=load('camera-controls/camera-controls.json');reveal=load('hand-reveal/hand-reveal-browser.json');batch=load('changed-poses/batch-poses-browser.json');inspection=load('inspection-gates/inspection-gate-browser.json')
source=ROOT/'src/features/practice/assets/hand-poses.json';sha=hashlib.sha256(source.read_bytes()).hexdigest()
expected=run['sourceLibrarySHA256'];source_bound=sha==expected
for record in [*trainers.values(),reveal,inspection]+([batch]if run['changedChordCaptures']else[]):
 assets=record.get('productionArtifactSHA256',{});source_bound &= bool(assets)and all(run['productionSnapshot'].get('assets/'+name)==value for name,value in assets.items())
 source_bound &= any(name.startswith('hand-poses-')and value==expected for name,value in assets.items())
counts={e:{'cases':len(r.get('checks',[])),'passedCases':sum(c.get('passed')is True for c in r.get('checks',[])),'passed':valid(r,21),'errors':errors(r),'browserVersion':r.get('browserVersion')}for e,r in trainers.items()}
original_count=sum(r.get('checks',0)for r in regression.get('runs',[]))
inspection_complete=valid(inspection,2) and all(row.get('chordsChecked')==42 and row.get('allowed',0)+row.get('blocked',0)==42 and row.get('sourceTransformsMatched')is True and len(row.get('views',[]))==6 for row in inspection.get('checks',[]))
checks={'trainers':all(v['passed']for v in counts.values()),'originalRegressions':regression.get('passed')is True and original_count==107,'cameraControls':valid(camera,2),'inspectionGates':inspection_complete,'handReveal':valid(reveal,4),'changedPoseCaptures':not run['changedChordCaptures']or(valid(batch,4)and batch.get('chords')==run['changedChordCaptures']),'matchingFrozenAssets':source_bound}
report={'scope':run['scope'],'checks':checks,'browserTrainers':counts,'originalRegressions':{'checks':original_count,'passed':checks['originalRegressions']},'inspectionGates':{'passed':inspection_complete,'sourceInspectionAllowed':inspection.get('sourceInspectionAllowed',[]),'engines':[{'engine':row.get('engine'),'checked':row.get('chordsChecked'),'allowed':row.get('allowed'),'blocked':row.get('blocked'),'views':len(row.get('views',[]))}for row in inspection.get('checks',[])]},'changedChordCaptures':run['changedChordCaptures'],'sourceLibrarySHA256':expected,'commandPlanPassed':run['commandPlanPassed'],'physicalIPadSafariTested':False,'teachingHandsApprovedByHarness':0,'limitations':['Linux WebKit does not establish physical iPad Safari or iPad GPU/FPS results.','Browser evidence does not certify skin collisions, anatomy or swept bone paths.','Only integrated changed poses get additional four-view capture loops; ordinary canonical screenshots remain test evidence.']}
report['passed']=run['commandPlanPassed']and all(checks.values())
(folder/'final-summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(not report['passed'])
