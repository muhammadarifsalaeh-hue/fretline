"""Additional real-surface pressure direction check, separate from mesh clearance.
Uses actual closest owned skin triangles; no anatomical/instructor approval.
"""
import argparse,hashlib,importlib.util,json,tempfile
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('direction',Path(__file__).with_name('contact-directions.py'));d=importlib.util.module_from_spec(s);s.loader.exec_module(d)
ap=argparse.ArgumentParser();ap.add_argument('--library',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();args.out.mkdir(parents=True,exist_ok=True);lib=json.loads(args.library.read_text());inventory=json.loads((ROOT/'docs/practice-complete-42/tests/candidate-inventory.json').read_text());keys=[r['id']for r in inventory if r['safeGeometryAndSupport']];context=d.f.load_context();rows=[]
for key in keys:
 with tempfile.TemporaryDirectory(prefix='fretline-owned-direction-')as tmp:row=d.measure(context,lib['poses'][key],Path(tmp))
 for t in row['contacts']:
  center=np.array(t['centerlinePointMm']);vector=np.array(t['palmarSkinPointMm'])-center;normal=np.array([0.,1.,center[2]/350]);normal/=np.linalg.norm(normal);t['boardOutwardComponentMm']=float(vector@normal);t['downwardPressurePossible']=t['boardOutwardComponentMm']>0
 row['contactDirectionPassed']=all(t['downwardPressurePossible']for t in row['contacts']);rows.append(row);(args.out/(key+'.json')).write_text(json.dumps(row,indent=2)+'\n');print('PRESSURE-DIRECTION',key,row['contactDirectionPassed'],flush=True)
report={'librarySHA256':hashlib.sha256(args.library.read_bytes()).hexdigest(),'modelSHA256':lib['assetSha256'],'count':len(rows),'passed':sum(r['contactDirectionPassed']for r in rows),'allPressureDirectionsPassed':all(r['contactDirectionPassed']for r in rows),'teachingApproval':False,'rows':rows};(args.out/'summary.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items()if k!='rows'}))
