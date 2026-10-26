"""Retry only trainer preparation failures on the exact same frozen build.

The initial reports remain failures. This never overwrites them or edits app
code. Wait for the initial serial browser plan to release all browsers first.
"""
from pathlib import Path
import argparse,hashlib,json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
ap=argparse.ArgumentParser();ap.add_argument('--initial',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
assert not args.output.exists() or not any(args.output.iterdir()),'Preserve earlier reports; use a fresh folder'
args.output.mkdir(parents=True,exist_ok=True)
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def snapshot():return {str(p.relative_to(ROOT/'dist')):digest(p)for p in sorted((ROOT/'dist').rglob('*'))if p.is_file()}
started=time.monotonic()
while not (args.initial/'run-summary.json').is_file():
 if time.monotonic()-started>3600:raise TimeoutError('Initial browser plan did not finish')
 time.sleep(3)
first=json.loads((args.initial/'run-summary.json').read_text());start=snapshot();source=ROOT/'src/features/practice/assets/hand-poses.json'
assert first['sourceUnchanged'] and first['buildUnchanged'] and first['completePlanExecuted']
assert start==first['productionSnapshot'] and digest(source)==first['sourceLibrarySHA256']
assert {r['name']for r in first['runs']if not r['passed']}=={'chromium','webkit'},'Review any additional initial failures separately'
for engine in ['chromium','webkit']:
 text=(args.initial/(engine+'.txt')).read_text()
 assert 'assert source.count(review_marker)==1' in text and 'AssertionError' in text,'This retry is limited to the identified harness anchor failure'
env=dict(os.environ)
for k,v in {'PLAYWRIGHT_BROWSERS_PATH':'/tmp/fretline-browser-engines','PLAYWRIGHT_SKIP_VALIDATE_HOST_REQUIREMENTS':'1','XDG_CACHE_HOME':'/tmp/fretline-webkit-cache','XDG_CONFIG_HOME':'/tmp/fretline-webkit-config','GSETTINGS_BACKEND':'memory'}.items():env.setdefault(k,v)
libs='/tmp/fretline-webkit-libs/usr/lib/x86_64-linux-gnu'
if Path(libs).is_dir():env['LD_LIBRARY_PATH']=libs+(':'+env['LD_LIBRARY_PATH']if env.get('LD_LIBRARY_PATH')else'')
result={'reason':'Initial adapter anchor matched both opening and closing assertions; changed to the unique opening-plus-canvas context. No app or expected behavior changed.','initialReports':str(args.initial),'sourceLibrarySHA256':first['sourceLibrarySHA256'],'productionSnapshot':start,'adapterSha256':digest(HERE/'run-trainer-settled.py'),'runs':[]}
for engine in ['chromium','webkit']:
 command=[sys.executable,str(HERE/'run-trainer-settled.py'),'--url',first['url'],'--engine',engine,'--output',str(args.output/engine)]
 with (args.output/(engine+'.txt')).open('w')as f:ran=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 result['runs'].append({'name':engine,'command':command,'returncode':ran.returncode,'passed':ran.returncode==0});print(engine,ran.returncode,flush=True)
result['sourceUnchanged']=digest(source)==first['sourceLibrarySHA256'];result['buildUnchanged']=start==snapshot();result['passed']=all(r['passed']for r in result['runs'])and result['sourceUnchanged']and result['buildUnchanged']
(args.output/'run-summary.json').write_text(json.dumps(result,indent=2)+'\n');raise SystemExit(not result['passed'])
