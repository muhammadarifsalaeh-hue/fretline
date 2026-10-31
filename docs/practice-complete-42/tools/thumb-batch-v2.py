"""Preserve every fretting bone while repairing real posterior thumb support."""
import argparse,copy,gzip,hashlib,importlib.util,json,subprocess,traceback
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('tool',Path(__file__).with_name('support-thumb.py'));tool=importlib.util.module_from_spec(s);s.loader.exec_module(tool)
f=tool.f
s=importlib.util.spec_from_file_location('full',Path(__file__).with_name('fit-pressure-v4.py'));full=importlib.util.module_from_spec(s);s.loader.exec_module(full)
s=importlib.util.spec_from_file_location('selector',Path(__file__).with_name('select-eligible.py'));selector=importlib.util.module_from_spec(s);s.loader.exec_module(selector)
ss=importlib.util.spec_from_file_location('measure',Path(__file__).with_name('measure-pose.py'));measure=importlib.util.module_from_spec(ss);ss.loader.exec_module(measure)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--seed',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--prior-audit',type=Path,action='append',default=[]);args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True);context=f.load_context();meter=measure.Measurements();base=copy.deepcopy(context['library']);seed=json.loads(args.seed.read_text());original=copy.deepcopy(seed);key=seed['chordId'];constraints={'kind':'authoring-constraints-not-an-audit','assetSha256':context['model_sha'],'self':{'pairs':[]},'guitar':{'pairs':[]},'sourceAuditFiles':[]};seen={'self':set(),'guitar':set()};history=[]
 def add_report(file):
  report=json.loads(file.read_text());r=report['rows'][0];rawfile=file.parent/r['rawEvidence']
  with gzip.open(rawfile,'rt')as stream:raw=json.load(stream)
  constraints['sourceAuditFiles'].append({'report':str(file),'rawSHA256':sha(rawfile),'poseTransformSHA256':raw['poseTransformSha256']})
  for kind in ['self','guitar']:
   for pair in raw.get(kind,{}).get('pairs',[]):
    signature=tuple(tuple(sorted(v))for v in pair['vertices'])
    if signature not in seen[kind]:seen[kind].add(signature);constraints[kind]['pairs'].append(pair)
 for file in args.prior_audit:add_report(file)
 for i in range(5):
  folder=args.out/('round-'+str(i));folder.mkdir(exist_ok=True);evidence=None
  if constraints['sourceAuditFiles']:
   constraints['poseTransformSha256']=f.gate.transform_hash(seed);evidence=folder/'constraints.json.gz'
   with gzip.open(evidence,'wt')as stream:json.dump(constraints,stream)
  if(folder/'candidate.json').exists():candidate=json.loads((folder/'candidate.json').read_text())
  else:candidate=tool.support(context,context['chords'][key],seed,folder,evidence)
  assert candidate['root']==original['root']
  for name,bone in original['bones'].items():
   if not name.startswith('finger1-'):assert candidate['bones'][name]==bone,'A fretting bone changed'
  report_file=folder/'audit/summary.json';proposal=folder/'proposal-library.json'
  if not report_file.exists():
   with(folder/'audit.log').open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('check-geometry.py')),'--library',str(proposal),'--chords',key,'--require','','--output',str(report_file.parent)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  report=json.loads(report_file.read_text());row=report['rows'][0];metrics=candidate['thumbSupport']['measurements'];support_measurement=meter.measure(candidate);passed=row['geometricPassed'] and support_measurement['thumbSupportPassed'] and support_measurement['jointPlausibilityPassed']
  history.append({'round':i,'geometry':row,'support':metrics,'measuredSupportWitness':support_measurement,'audit':str(report_file.relative_to(ROOT))});print('THUMB',key,'round',i,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'passed',passed,flush=True)
  if passed:
   selected,decisions=selector.select(full,base,json.loads(proposal.read_text()),report,sha(proposal),context['model_sha'],context['chord_sha'],[key]);assert decisions[0]['selected'];(args.out/'selected.json').write_text(json.dumps(selected['poses'][key],ensure_ascii=False,indent=2)+'\n');break
  add_report(report_file);seed=copy.deepcopy(candidate)
  witness=support_measurement.get('thumbSupportWitness')
  if witness and support_measurement['thumbSupportPassed']:
   point=np.array(witness['neckBackPointMm']);_,normal,_=full.nearest_surface(point[None,:],meter.back,k=min(64,len(meter.back)));normal=normal[0];normal*=1 if normal[1]<0 else -1
   seed.setdefault('thumbSupport',{})['targetMm']=(point+normal*.4).tolist()
   print('REANCHOR',key,'to measured posterior neck witness; geometry gates unchanged',flush=True)
 result={'id':key,'selected':passed,'thumbSupportPassed':passed,'frettingBonesAndRootIdentical':True,'teachingApproved':False,'proposalFile':str(proposal.relative_to(ROOT)),'auditReport':str(report_file.relative_to(ROOT)),'history':history};(args.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
