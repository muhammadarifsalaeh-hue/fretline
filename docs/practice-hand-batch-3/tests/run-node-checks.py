"""Record serial required core checks and unchanged historical checks separately."""
import json,os,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-hand-batch-3';env=dict(os.environ);env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
commands=[('catalog',['npm','run','catalog:check']),('images',['npm','run','images:check']),('practice',['npm','run','practice:check']),('music',['node','docs/practice-trainer/tests/chord-audit.test.mjs']),('hand-runtime',['node','scripts/check-hand-runtime.mjs']),('pressed-strings',['node','docs/practice-trainer/tests/fretted-strings.test.mjs']),('fingerprint',['node','scripts/practice/check-fingerprint.mjs']),('hand-reveal',['node','scripts/practice/check-hand-reveal.mjs']),('negative-geometry',['python','scripts/practice/test-hand-geometry.py'])]
summary={'core':[],'legacy':[]}
for name,command in commands:
 with (OUT/(name+'-check.txt')).open('w')as f:r=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 summary['core'].append({'name':name,'command':command,'returncode':r.returncode,'passed':r.returncode==0});print(name,r.returncode,flush=True)
legacy=OUT/'legacy-static';legacy.mkdir(exist_ok=True)
for phase in range(4,10):
 command=['npm','run',f'phase{phase}:check']
 with (legacy/f'phase{phase}.txt').open('w')as f:r=subprocess.run(command,cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 summary['legacy'].append({'name':f'phase{phase}','command':command,'returncode':r.returncode,'passed':r.returncode==0});print('legacy',phase,r.returncode,flush=True)
summary['corePassed']=all(r['passed']for r in summary['core']);summary['allLegacyPassed']=all(r['passed']for r in summary['legacy'])
(OUT/'node-checks.json').write_text(json.dumps(summary,indent=2)+'\n');raise SystemExit(not summary['corePassed'])
