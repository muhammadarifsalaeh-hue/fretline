"""Frozen-build acceptance; stronger rejected-hand gate, serial browsers, changed poses only.

Build/start preview externally. Every run uses a fresh output folder, so failures
cannot be overwritten by a successful retry. No app, chord, model or gate edits.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys
ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser()
ap.add_argument('--url',default='http://127.0.0.1:5430')
ap.add_argument('--output',type=Path,default=HERE/'reports'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ'))
ap.add_argument('--freeze-sha',required=True,help='Expected current runtime hand library SHA-256')
ap.add_argument('--changed-chords',default='',help='Only integrated changed chord IDs receive an extra four-view capture loop')
ap.add_argument('--cases',default='chromium,webkit,regressions,camera-controls,changed-poses,inspection-gates,hand-reveal')
args=ap.parse_args();args.output=args.output.resolve()
assert not args.output.exists() or not any(args.output.iterdir()), 'Use a fresh output path; preserve earlier failure evidence'
args.output.mkdir(parents=True,exist_ok=True)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot():
 return {str(p.relative_to(ROOT/'dist')):digest(p)for p in sorted((ROOT/'dist').rglob('*'))if p.is_file()}
source=ROOT/'src/features/practice/assets/hand-poses.json';library=json.loads(source.read_text())
assert digest(source)==args.freeze_sha, 'Freeze SHA differs from current runtime library'
assert len(library['poses'])==42
changed=list(filter(None,args.changed_chords.split(',')))
assert len(changed)==len(set(changed)) and set(changed)<=set(library['poses'])
start=snapshot();assert start, 'Build production assets before browser QA'
assert any(name.startswith('assets/hand-poses-')and value==args.freeze_sha for name,value in start.items()), 'Production build must contain frozen current library'
env=dict(os.environ)
for name,value in {'PLAYWRIGHT_BROWSERS_PATH':'/tmp/fretline-browser-engines','PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS':'1','XDG_CACHE_HOME':'/tmp/fretline-webkit-cache','XDG_CONFIG_HOME':'/tmp/fretline-webkit-config','GSETTINGS_BACKEND':'memory'}.items():env.setdefault(name,value)
libs='/tmp/fretline-webkit-libs/usr/lib/x86_64-linux-gnu'
if Path(libs).is_dir():env['LD_LIBRARY_PATH']=libs+(':'+env['LD_LIBRARY_PATH']if env.get('LD_LIBRARY_PATH')else'')
commands=[]
for engine in ['chromium','webkit']:
 commands.append((engine,[sys.executable,str(HERE/'run-trainer-settled.py'),'--url',args.url,'--engine',engine,'--output',str(args.output/engine)]))
commands += [('regressions',[sys.executable,str(ROOT/'docs/practice-trainer/tests/run-regressions.py'),'--url',args.url,'--output',str(args.output/'regressions')]),('camera-controls',[sys.executable,str(ROOT/'docs/practice-trainer/tests/camera-controls.py'),'--url',args.url,'--output',str(args.output/'camera-controls')])]
if changed:commands.append(('changed-poses',[sys.executable,str(HERE/'batch-poses-browser.py'),'--url',args.url,'--output',str(args.output/'changed-poses'),'--chords',','.join(changed)]))
commands.append(('inspection-gates',[sys.executable,str(HERE/'inspection-gate-browser.py'),'--url',args.url,'--output',str(args.output/'inspection-gates')]))
commands.append(('hand-reveal',[sys.executable,str(HERE/'hand-reveal-browser.py'),'--url',args.url,'--output',str(args.output/'hand-reveal')]))
required={name for name,_ in commands};selected=set(args.cases.split(','));assert selected<=required|{'changed-poses'}
report={'scope':'Frozen browser/functional acceptance, separate from endpoint anatomy and physical iPad Safari', 'url':args.url,'sourceLibrarySHA256':args.freeze_sha,'productionSnapshot':start,'changedChordCaptures':changed,'runs':[],'physicalIPadSafariTested':False,'teachingHandsApprovedByHarness':0}
(args.output/'start.json').write_text(json.dumps(report,indent=2)+'\n')
for name,command in commands:
 if name not in selected:continue
 with (args.output/(name+'.txt')).open('w')as output:r=subprocess.run(command,cwd=ROOT,env=env,stdout=output,stderr=subprocess.STDOUT)
 row={'name':name,'command':command,'returncode':r.returncode,'passed':r.returncode==0};report['runs'].append(row)
 (args.output/'run-progress.json').write_text(json.dumps(report,indent=2)+'\n');print(('PASS'if row['passed']else'FAIL'),name,flush=True)
report['sourceUnchanged']=digest(source)==args.freeze_sha;report['buildUnchanged']=start==snapshot()
report['completePlanExecuted']={row['name']for row in report['runs']}==required
report['executedCommandsPassed']=all(row['passed']for row in report['runs'])
report['commandPlanPassed']=report['completePlanExecuted'] and report['executedCommandsPassed'] and report['sourceUnchanged'] and report['buildUnchanged']
(args.output/'run-summary.json').write_text(json.dumps(report,indent=2)+'\n')
# Independent summary verifies expected actual case counts, not only exit codes.
result=subprocess.run([sys.executable,str(HERE/'summarize-final.py'),'--reports',str(args.output)],cwd=ROOT,env=env)
raise SystemExit(0 if report['commandPlanPassed'] and result.returncode==0 else 1)
