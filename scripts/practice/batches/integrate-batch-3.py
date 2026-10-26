#!/usr/bin/env python3
"""Promote exact-mesh acceptance only, never approve a teaching pose.

Only listed candidates are accepted; the central music and model remain fixed.
A separate full-library audit must be rerun after writing runtime JSON.
"""
import copy,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/practice-hand-batch-3'
ITEMS={'Em7':('candidate.json','audit/summary.json'),'E7':('candidate.json','audit/summary.json'),'Fmaj7':('refined.json','refined-audit/summary.json'),'Dm':('surgical.json','surgical-audit/summary.json')}
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def transform(p):return hashlib.sha256(json.dumps({'root':p['root'],'bones':p['bones']},sort_keys=True,separators=(',',':')).encode()).hexdigest()
def main():
 path=ROOT/'src/features/practice/assets/hand-poses.json';lib=json.loads(path.read_text());original=copy.deepcopy(lib);rows=[]
 assert len(lib['poses'])==42
 for key,(candidatefile,auditfile) in ITEMS.items():
  candidate_path=OUT/key/candidatefile;audit_path=OUT/key/auditfile
  candidate=json.loads(candidate_path.read_text());audit=json.loads(audit_path.read_text());row=next(r for r in audit['rows'] if r['id']==key)
  assert candidate['chordId']==key and candidate['assetSha256']==lib['assetSha256']==audit['assetSha256']
  assert sha(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb')==lib['assetSha256']
  assert sha(ROOT/'src/features/practice/data/chords.js')==audit['sourceChordSha256']
  assert row['poseTransformSha256']==transform(candidate) and row['geometricPassed'] is True
  assert row['skinAndClothSelfCrossingPairs']==0 and row['woodSamplesInsideOver002Mm']==0
  assert row['guitar']['status']=='tested' and row['guitar']['crossingPairs']==0
  assert row['contacts'] and all(t['passed'] for t in row['contacts'])
  assert all(s['openStringPassed'] is not False for s in row['strings'])
  candidate['status']='needs-review';candidate['reviewed']=False
  candidate['audit']={'collisionPassed':True,'contactPassed':True,'anatomyPassed':False,'multiViewReviewed':False,'batchEvidence':str(audit_path.relative_to(ROOT))}
  candidate['reason']={'th':'ผ่านการตรวจตำแหน่งนิ้วและการชนเชิงเรขาคณิตแล้ว ยังรอตรวจความเป็นธรรมชาติของมือก่อนใช้สอน','en':'Geometric contact and collision checks pass. Natural hand presentation still needs review before teaching approval.'}
  lib['poses'][key]=candidate;rows.append({'id':key,'candidateSha256':sha(candidate_path),'transformSha256':transform(candidate),'evidence':str(audit_path.relative_to(ROOT))})
 assert all(lib['poses'][key]==p for key,p in original['poses'].items() if key not in ITEMS)
 path.write_text(json.dumps(lib,ensure_ascii=False,separators=(',',':'))+'\n')
 (OUT/'integration.json').write_text(json.dumps({'base':'74c2076','items':rows,'librarySha256':sha(path),'teachingApprovalsAdded':0,'otherPosesUnchanged':True},indent=2)+'\n')
 print(json.dumps({'integrated':list(ITEMS),'teachingApprovals':0}))
if __name__=='__main__':main()
