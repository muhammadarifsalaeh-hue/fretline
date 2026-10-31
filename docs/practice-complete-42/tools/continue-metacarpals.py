"""Continue actual constraint generation after a saved full-mesh rejection."""
import argparse,copy,gzip,hashlib,importlib.util,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v5.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
s=importlib.util.spec_from_file_location('selector',Path(__file__).with_name('select-eligible.py'));selector=importlib.util.module_from_spec(s);s.loader.exec_module(selector)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--result',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--rounds',type=int,default=4);ap.add_argument('--seconds',type=int,default=130);args=ap.parse_args();args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=True);source=json.loads(args.result.read_text());key=source['id'];context=f.load_context();base=copy.deepcopy(context['library']);proposal_path=ROOT/source['proposalFile'];seed=json.loads(proposal_path.read_text())['poses'][key];report_path=ROOT/source['auditReport'];row=json.loads(report_path.read_text())['rows'][0];constraints={'kind':'authoring-constraints-not-an-audit','assetSha256':context['model_sha'],'self':{'pairs':[]},'guitar':{'pairs':[]},'sourceAuditFiles':[]};seen={'self':set(),'guitar':set()};history=[]
 def add(file):
  report=json.loads(file.read_text());rawfile=file.parent/report['rows'][0]['rawEvidence']
  with gzip.open(rawfile,'rt')as stream:raw=json.load(stream)
  constraints['sourceAuditFiles'].append({'path':str(rawfile),'sha256':sha(rawfile),'poseTransformSHA256':raw['poseTransformSha256']})
  for kind in ['self','guitar']:
   for pair in raw.get(kind,{}).get('pairs',[]):
    signature=tuple(tuple(sorted(v))for v in pair['vertices'])
    if signature not in seen[kind]:seen[kind].add(signature);constraints[kind]['pairs'].append(pair)
 for record in source['history']:
  if record.get('report'):add(ROOT/record['report'])
 if not constraints['sourceAuditFiles']:add(report_path)
 for i in range(args.rounds):
  folder=args.out/('round-'+str(i));folder.mkdir(exist_ok=True);constraints['poseTransformSha256']=f.gate.transform_hash(seed);evidence=folder/'constraints.json.gz'
  with gzip.open(evidence,'wt')as stream:json.dump(constraints,stream)
  if(folder/'candidate.json').exists():candidate=json.loads((folder/'candidate.json').read_text());metrics=json.loads((folder/'metrics.json').read_text())
  else:candidate,metrics=f.fit(context,context['chords'][key],seed,folder,iterations=150,yaw=0,root_free=True,evidence=evidence,radius=10,exact_polish=row['skinAndClothSelfCrossingPairs']==0,max_seconds=args.seconds,all_fingers=True,full_polish=True)
  proposal=copy.deepcopy(base);proposal['poses'][key]=candidate;proposal_file=folder/'proposal-library.json';proposal_file.write_text(f.previous.frozen_json(proposal));report_file=folder/'audit/summary.json'
  if not report_file.exists():
   with(folder/'audit.log').open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('check-geometry.py')),'--library',str(proposal_file),'--chords',key,'--require','','--output',str(report_file.parent)],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
  report=json.loads(report_file.read_text());row=report['rows'][0];history.append({'round':i,'metrics':metrics,'row':row,'report':str(report_file.relative_to(ROOT))});print('CONTINUE',key,'round',i,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'contacts',sum(c['passed']for c in row['contacts']),'/',len(row['contacts']),'barre',row.get('barreCoverage'),'passed',row['geometricPassed'],flush=True)
  if row['geometricPassed']:
   selected,decisions=selector.select(f,base,proposal,report,sha(proposal_file),context['model_sha'],context['chord_sha'],[key]);assert decisions[0]['selected'];(args.out/'selected.json').write_text(json.dumps(selected['poses'][key],ensure_ascii=False,indent=2)+'\n');break
  add(report_file);seed=candidate
 result={'id':key,'selected':row['geometricPassed'],'teachingApproved':False,'continuedFrom':str(args.result),'history':history,'proposalFile':str(proposal_file.relative_to(ROOT)),'auditReport':str(report_file.relative_to(ROOT))};(args.out/'result.json').write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
