"""Fresh final core/legacy checks; legacy failures remain separate outcomes."""
from pathlib import Path
import subprocess,json
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent
commands=[('catalog',['npm','run','catalog:check']),('images',['npm','run','images:check']),('practice',['npm','run','practice:check']),('music',['node','docs/practice-trainer/tests/chord-audit.test.mjs']),('hand-runtime',['node','scripts/check-hand-runtime.mjs']),('pressed-strings',['node','docs/practice-trainer/tests/fretted-strings.test.mjs']),('fingerprint',['node','scripts/practice/check-fingerprint.mjs']),('reveal',['node','scripts/practice/check-hand-reveal.mjs']),('camera',['node','scripts/practice/check-final-camera.mjs'])]
result={'core':[],'legacy':[]}
for name,args in commands:
 with (OUT/(name+'.txt')).open('w')as f:r=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 result['core'].append({'name':name,'command':args,'returncode':r.returncode,'passed':r.returncode==0});print(name,r.returncode,flush=True)
for phase in range(4,10):
 args=['npm','run',f'phase{phase}:check']
 with (OUT/f'phase{phase}.txt').open('w')as f:r=subprocess.run(args,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT)
 result['legacy'].append({'name':f'phase{phase}','command':args,'returncode':r.returncode,'passed':r.returncode==0});print('legacy',phase,r.returncode,flush=True)
result['corePassed']=all(r['passed']for r in result['core']);result['allLegacyPassed']=all(r['passed']for r in result['legacy']);(OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n');raise SystemExit(not result['corePassed'])
