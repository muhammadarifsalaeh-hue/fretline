"""Select only measured poses with canonical effective fingering and barre span.
Geometry/contact eligibility is separate from anatomy, images and human approval.
"""
import copy,hashlib,json,math,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def select(f,base,proposal,report,library_sha,model_sha,chord_sha,expected):
 assert hashlib.sha256(f.previous.frozen_json(proposal).encode()).hexdigest()==library_sha==report['librarySnapshotSha256']
 assert report['assetSha256']==model_sha and report['sourceChordSha256']==chord_sha
 assert report['count']==len(report['rows'])==len(expected)and {r['id']for r in report['rows']}==set(expected)
 assert report['testSuitePassed']and not report['errors']and report['geometricPassed']==sum(r['geometricPassed']is True for r in report['rows'])
 assert set(base['poses'])==set(proposal['poses'])and len(base['poses'])==42
 assert all(proposal['poses'][key]==base['poses'][key]for key in base['poses']if key not in expected),'Unrelated pose records changed'
 assert proposal['assetSha256']==base['assetSha256']==model_sha and proposal['rigSignature']==base['rigSignature']
 assert report['originalTriangleCheckerSHA256']==hashlib.sha256((ROOT/'scripts/practice/audit-hand-self-collisions.py').read_bytes()).hexdigest()
 chords={c['id']:c for c in json.loads(subprocess.check_output(['node','--input-type=module','-e',"import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"],cwd=ROOT))};result=copy.deepcopy(base);decisions=[]
 for row in report['rows']:
  key=row['id'];pose=proposal['poses'][key];chord=chords[key];assert row['poseTransformSha256']==f.gate.transform_hash(pose) and pose['chordId']==key
  assert row['pressureSHA256']==hashlib.sha256(json.dumps(pose.get('pressOffsetsMm'),sort_keys=True,separators=(',',':')).encode()).hexdigest()
  musical=f.effective_contacts(chord)if 'pressOffsetsMm'in pose else f.gate.contacts(chord)
  expected_contacts=sorted((t['finger'],t['string'],t['fret'],t['kind'])for t in musical);actual=sorted((t['finger'],t['string'],t['fret'],t['kind'])for t in row['contacts'])
  contact_ok=actual==expected_contacts and all(t['passed']is True and all(type(t[k])is int for k in ['finger','string','fret']) and math.isfinite(t['actualOwnerPalmarSkinClearanceMm'])and -.00001<=t['actualOwnerPalmarSkinClearanceMm']<=.12 for t in row['contacts'])
  strings={s['number']:s for s in row['strings']};string_ok=len(row['strings'])==6 and set(strings)==set(range(1,7))and all(s['fret']==chord['frets'][6-n]and math.isfinite(s['wholeSkinClearanceMm'])and(s['openStringPassed']is True and s['wholeSkinClearanceMm']>=.2 if s['fret']==0 else s['openStringPassed']is None)for n,s in strings.items())
  coverage_ok=True
  if 'pressOffsetsMm'in pose:
   assert row['contactSemantics']=='effective-fingering-v1'
   expected_coverage=sorted((t['finger'],t['string'],t['fret'])for t in f.gate.contacts(chord)if t['kind']=='barre'and chord['frets'][6-t['string']]!=t['fret'])
   actual_coverage=sorted((t['finger'],t['string'],t['fret'])for t in row['barreCoverage']);coverage_ok=actual_coverage==expected_coverage and all(t['passed']is True and math.isfinite(t['palmarClearanceMm'])and -.00001<=t['palmarClearanceMm']<=3 and t['effectiveFinger']==chord['fingers'][6-t['string']]and t['effectiveFret']==chord['frets'][6-t['string']]for t in row['barreCoverage'])
  def finite(values,n):return isinstance(values,list)and len(values)==n and all(type(v)in(int,float)and math.isfinite(v)for v in values)
  def quat(q):return finite(q,4)and abs(math.sqrt(sum(v*v for v in q))-1)<.02
  pose_ok=finite(pose.get('root',{}).get('positionMm'),3)and quat(pose.get('root',{}).get('quaternion'))and set(pose.get('bones',{}))==set(base['poses'][key]['bones'])and all(quat(v.get('quaternion'))for v in pose['bones'].values())
  pressure_ok=True
  if 'pressOffsetsMm'in pose:
   offsets=pose['pressOffsetsMm'];wanted={f"{t['string']}:{t['fret']}"for t in f.effective_contacts(chord)}
   pressure_ok=isinstance(offsets,dict)and set(offsets)==wanted
   if pressure_ok:
    for t in f.effective_contacts(chord):
     v=offsets[f"{t['string']}:{t['fret']}"];gap=f.m.fret_x(t['fret'])-f.m.fret_x(t['fret']-1)
     pressure_ok=pressure_ok and type(v)in(int,float)and math.isfinite(v)and 1.5<=v<=min(24,gap-5)
  ok=pose_ok and pressure_ok and row['geometricPassed']is True and row['voicing']==chord['voicing']and type(row['skinAndClothSelfCrossingPairs'])is int and row['skinAndClothSelfCrossingPairs']==0 and type(row['woodSamplesInsideOver002Mm'])is int and row['woodSamplesInsideOver002Mm']==0 and math.isfinite(row['maximumWoodDepthMm'])and 0<=row['maximumWoodDepthMm']<=.02 and type(row['woodSamples'])is int and row['woodSamples']>0 and row['guitar'].get('status')=='tested'and type(row['guitar']['crossingPairs'])is int and row['guitar']['crossingPairs']==0 and contact_ok and string_ok and coverage_ok
  if ok:
   p=copy.deepcopy(pose);p['status']='needs-review';p['reviewed']=False;p['audit']={'collisionPassed':True,'contactPassed':True,'anatomyPassed':False,'multiViewReviewed':False};result['poses'][key]=p
  decisions.append({'id':key,'selected':ok,'geometryOnly':True,'teachingApproved':False})
 return result,decisions
