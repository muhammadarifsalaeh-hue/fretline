#!/usr/bin/env python3
"""Verify the original product site, music and rig remain exactly unchanged."""
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];BASE='74c2076';OUT=ROOT/'docs/practice-hand-batch-3'
def original(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 prior=json.loads((ROOT/'docs/practice-hand-batch-2/protected-site.json').read_text());protected=[]
 for row in prior['files']:
  name=row['path'];data=(ROOT/name).read_bytes();protected.append({'path':name,'sha256':sha(data),'unchanged':data==original(name)})
 sources=[]
 for name in ['src/features/practice/data/chords.js','src/features/practice/assets/makehuman-left-arm-sleeved.glb','src/features/practice/assets/makehuman-left-arm.metadata.json','docs/practice-trainer/models/authoring/rig-data.json']:
  data=(ROOT/name).read_bytes();sources.append({'file':name,'sha256':sha(data),'unchanged':data==original(name)})
 old=json.loads(original('src/features/practice/assets/hand-poses.json'));new=json.loads((ROOT/'src/features/practice/assets/hand-poses.json').read_text());integration=json.loads((OUT/'integration.json').read_text());changed={r['id'] for r in integration['items']}
 assert set(new['poses'])==set(old['poses']) and len(new['poses'])==42
 others=[{'id':key,'unchanged':value==new['poses'][key]} for key,value in old['poses'].items() if key not in changed]
 assert all(r['unchanged'] for r in protected+sources+others)
 (OUT/'protected-site.json').write_text(json.dumps({'baseline':BASE,'count':len(protected),'allUnchanged':True,'files':protected},indent=2)+'\n')
 (OUT/'source-preservation.json').write_text(json.dumps({'baseline':BASE,'sources':sources,'otherPoseRecords':others,'onlyIntegratedPosesChanged':True,'allUnchanged':True},indent=2)+'\n')
 print(json.dumps({'protectedSiteFiles':len(protected),'musicAndRigFiles':len(sources),'unchangedOtherPoseRecords':len(others),'passed':True}))
if __name__=='__main__':main()
