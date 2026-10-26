#!/usr/bin/env python3
"""Actual source-bound audit-selection rejection regressions; no runtime edits."""
import copy,hashlib,importlib.util,json,subprocess,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('central_solver',Path(__file__).with_name('solve.py'));s=importlib.util.module_from_spec(spec);spec.loader.exec_module(s)

class AuditSelection(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.library_path=ROOT/'src/features/practice/assets/hand-poses.json';cls.original=cls.library_path.read_bytes();cls.library=json.loads(cls.original)
  old=json.loads(subprocess.check_output(['git','show','74c2076:src/features/practice/assets/hand-poses.json'],cwd=ROOT))
  cls.base=copy.deepcopy(cls.library);cls.base['poses']['Dm']=old['poses']['Dm']
  assert s.transform_hash(cls.base['poses']['Dm'])!=s.transform_hash(cls.library['poses']['Dm'])
  cls.audit=json.loads((ROOT/'docs/practice-hand-batch-3/geometry/summary.json').read_text())
 @classmethod
 def tearDownClass(cls):
  assert cls.library_path.read_bytes()==cls.original,'Tests must never mutate the runtime library'
 def inputs(self):
  proposal=copy.deepcopy(self.library);report=copy.deepcopy(self.audit)
  report['rows']=[r for r in report['rows']if r['id']=='Dm'];report['count']=1;report['geometricPassed']=1;report['all42GeometricPassed']=False
  return proposal,report
 def run_selection(self,proposal,report,**kwargs):
  declared=hashlib.sha256(s.frozen_json(proposal).encode()).hexdigest()
  return s.select_audited_replacements(self.base,proposal,report,kwargs.get('library_sha',declared),kwargs.get('model_sha',self.library['assetSha256']),kwargs.get('chord_sha',self.audit['sourceChordSha256']),kwargs.get('expected_ids',['Dm']))
 def rejected(self,proposal,report,**kwargs):
  try:result,decisions=self.run_selection(proposal,report,**kwargs)
  except (AssertionError,KeyError,TypeError,ValueError):return
  self.assertEqual(result,self.base)
  self.assertFalse(any(r['selected']for r in decisions))
 def test_real_pass_can_replace_real_rejected_pose_without_teaching_approval(self):
  proposal,report=self.inputs();before=copy.deepcopy(proposal);result,decisions=self.run_selection(proposal,report)
  self.assertTrue(decisions[0]['selected']);self.assertEqual(s.transform_hash(result['poses']['Dm']),s.transform_hash(self.library['poses']['Dm']))
  self.assertEqual(proposal,before);self.assertEqual(result['poses']['Dm']['status'],'needs-review');self.assertIs(result['poses']['Dm']['reviewed'],False)
  self.assertIs(result['poses']['Dm']['audit']['anatomyPassed'],False);self.assertIs(result['poses']['Dm']['audit']['multiViewReviewed'],False)
  self.assertTrue(all(result['poses'][k]==v for k,v in self.base['poses'].items()if k!='Dm'))
 def test_forged_verified_label_is_stripped_even_for_a_geometric_endpoint(self):
  proposal,report=self.inputs();proposal['poses']['Dm']['status']='verified';proposal['poses']['Dm']['reviewed']=True;proposal['poses']['Dm']['audit']={gate:True for gate in s.GATES}
  report['librarySnapshotSha256']=hashlib.sha256(s.frozen_json(proposal).encode()).hexdigest();result,decisions=self.run_selection(proposal,report)
  self.assertTrue(decisions[0]['selected']);self.assertEqual(result['poses']['Dm']['status'],'needs-review');self.assertFalse(result['poses']['Dm']['reviewed']);self.assertFalse(result['poses']['Dm']['audit']['anatomyPassed'])
 def test_stale_library_model_or_musical_source_hash_is_rejected(self):
  for field in ['librarySnapshotSha256','assetSha256','sourceChordSha256']:
   with self.subTest(field=field):
    p,r=self.inputs();r[field]='0'*64;self.rejected(p,r)
  p,r=self.inputs();self.rejected(p,r,library_sha='0'*64)
 def test_actual_transform_change_invalidates_old_physical_evidence(self):
  p,r=self.inputs();p['poses']['Dm']['root']['positionMm'][0]+=.01;r['librarySnapshotSha256']=hashlib.sha256(s.frozen_json(p).encode()).hexdigest();self.rejected(p,r)
 def test_missing_duplicate_or_wrong_chord_rows_are_rejected(self):
  for mode in ['missing','duplicate','wrong']:
   with self.subTest(mode=mode):
    p,r=self.inputs()
    if mode=='missing':r['rows']=[];r['count']=0;r['geometricPassed']=0
    elif mode=='duplicate':r['rows']*=2;r['count']=2;r['geometricPassed']=2
    else:r['rows'][0]['id']='C'
    self.rejected(p,r)
 def test_every_changed_pose_requires_its_own_exact_audit(self):
  p,r=self.inputs();p['poses']['E7']['root']['positionMm'][0]+=1;r['librarySnapshotSha256']=hashlib.sha256(s.frozen_json(p).encode()).hexdigest();self.rejected(p,r)
 def test_missing_or_wrong_owner_fret_contact_is_rejected(self):
  for mode in ['missing','finger','string','fret','flag']:
   with self.subTest(mode=mode):
    p,r=self.inputs();contact=r['rows'][0]['contacts'][0]
    if mode=='missing':r['rows'][0]['contacts'].pop()
    elif mode=='flag':contact['passed']='true'
    else:contact[mode]=99
    self.rejected(p,r)
 def test_contact_and_open_string_thresholds_are_not_relaxed(self):
  for mode in ['tooFar','insideString','openTooClose']:
   with self.subTest(mode=mode):
    p,r=self.inputs();row=r['rows'][0]
    if mode=='openTooClose':next(t for t in row['strings']if t['fret']==0)['wholeSkinClearanceMm']=.199999
    else:row['contacts'][0]['actualOwnerPalmarSkinClearanceMm']=.120001 if mode=='tooFar'else-.00002
    self.rejected(p,r)
 def test_guitar_wood_or_self_crossings_cannot_be_hidden_by_a_pass_label(self):
  for field in ['self','wood','guitar','maxDepth','booleanCounter']:
   with self.subTest(field=field):
    p,r=self.inputs();row=r['rows'][0]
    if field=='self':row['skinAndClothSelfCrossingPairs']=1
    elif field=='wood':row['woodSamplesInsideOver002Mm']=1
    elif field=='guitar':row['guitar']['crossingPairs']=1
    elif field=='maxDepth':row['maximumWoodDepthMm']=.020001
    else:row['skinAndClothSelfCrossingPairs']=False
    self.rejected(p,r)
 def test_all_six_unique_actual_string_states_are_required(self):
  for mode in ['missing','duplicate','wrongFret','missingOpenFlag']:
   with self.subTest(mode=mode):
    p,r=self.inputs();strings=r['rows'][0]['strings']
    if mode=='missing':strings.pop()
    elif mode=='duplicate':strings[0]['number']=strings[1]['number']
    elif mode=='wrongFret':strings[0]['fret']=99
    else:next(t for t in strings if t['fret']==0)['openStringPassed']=None
    self.rejected(p,r)
 def test_incomplete_or_inconsistent_audit_completion_is_rejected(self):
  for mode in ['suite','errors','count']:
   with self.subTest(mode=mode):
    p,r=self.inputs()
    if mode=='suite':r['testSuitePassed']=False
    elif mode=='errors':r['errors']=['actual failure']
    else:r['geometricPassed']=0
    self.rejected(p,r)
 def test_failed_numerical_candidate_preserves_the_original(self):
  p,r=self.inputs();row=r['rows'][0];row['geometricPassed']=False;row['skinAndClothSelfCrossingPairs']=2;r['geometricPassed']=0
  self.rejected(p,r)
 def test_invalid_budget_or_chord_list_leaves_no_output_artifacts(self):
  cases=[['--max-evaluations','0'],['--max-evaluations','-1'],['--placement-weight','nan'],['--placement-weight','-1'],['--chords','C,C'],['--chords','does-not-exist']]
  with tempfile.TemporaryDirectory(prefix='fretline-central-cli-')as temp:
   for i,args in enumerate(cases):
    with self.subTest(args=args):
     output=Path(temp)/str(i);r=subprocess.run(['python',str(Path(__file__).with_name('solve.py')),'--output',str(output),*args],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
     self.assertEqual(r.returncode,2,r.stderr.decode());self.assertFalse(output.exists())
 def test_fresh_evidence_output_is_never_overwritten(self):
  with tempfile.TemporaryDirectory(prefix='fretline-central-protect-')as temp:
   output=Path(temp);sentinel=output/'existing-evidence.txt';sentinel.write_text('preserve this evidence')
   r=subprocess.run(['python',str(Path(__file__).with_name('solve.py')),'--output',temp],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
   self.assertEqual(r.returncode,2);self.assertEqual(sentinel.read_text(),'preserve this evidence')

if __name__=='__main__':unittest.main(verbosity=2)
