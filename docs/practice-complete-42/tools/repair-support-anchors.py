"""Re-anchor a nearly valid thumb to a witnessed real neck-back point.
No relaxed geometry limits, changed fretting fingers or assumed support.
"""
import importlib.util,json,subprocess
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3];s=importlib.util.spec_from_file_location('measure',Path(__file__).with_name('measure-pose.py'));m=importlib.util.module_from_spec(s);s.loader.exec_module(m);meter=m.Measurements()
base=ROOT/'.local-preview/practice-complete-42';out=base/'thumb-contact-polish'
for key,round_n in [('A7',1),('Asus2',2),('Amaj7',2)]:
 folder=out/key;folder.mkdir(parents=True,exist_ok=True);source=base/'thumb-final'/key/('round-'+str(round_n));pose=json.loads((source/'candidate.json').read_text());before=meter.measure(pose);w=before['thumbSupportWitness'];assert w and before['thumbSupportPassed'];a=np.array(w['palmarSkinPointMm']);b=np.array(w['neckBackPointMm']);d=a-b;assert d[1]<0,'Use an actual outward witness, never an interior anchor';target=b+d/np.linalg.norm(d)*.4;pose['thumbSupport']['targetMm']=target.tolist();file=folder/'seed.json';file.write_text(json.dumps(pose));(folder/'source.json').write_text(json.dumps({'source':str(source),'witness':before,'targetMm':target.tolist(),'onlyAuthoringTargetChanged':True},indent=2)+'\n')
 subprocess.run(['python',str(Path(__file__).with_name('thumb-batch.py')),'--seed',str(file),'--out',str(folder/'trials'),'--prior-audit',str(source/'audit/summary.json')],cwd=ROOT,check=True)
