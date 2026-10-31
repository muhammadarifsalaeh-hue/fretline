"""Resume authoring by chord against immutable musical/model sources.
Original exact mesh/contact checker is read and executed unchanged.
"""
import argparse,copy,gzip,hashlib,importlib.util,json,subprocess,traceback,time
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
s=importlib.util.spec_from_file_location('thumb',Path(__file__).with_name('relax-thumb.py'));thumb=importlib.util.module_from_spec(s);s.loader.exec_module(thumb)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def audit(base,p,folder):
 folder.mkdir(parents=True,exist_ok=True);lib=copy.deepcopy(base);lib['poses'][p['chordId']]=p;file=folder/'proposal-library.json';file.write_text(f.previous.frozen_json(lib))
 with(folder/'audit.log').open('w')as log:subprocess.run(['python',str(Path(__file__).with_name('check-geometry.py')),'--library',str(file),'--chords',p['chordId'],'--require','','--output',str(folder/'audit')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
 return json.loads((folder/'audit/summary.json').read_text()),file

def best_seeds():
 best={}
 for p in(ROOT/'.local-preview/practice-fingering').rglob('summary.json'):
  try:
   d=json.loads(p.read_text());file=p.parent.parent/'proposal-library.json'
   if not file.exists():continue
   lib=json.loads(file.read_text())
   for r in d.get('rows',[]):
    if 'skinAndClothSelfCrossingPairs'not in r or f.gate.transform_hash(lib['poses'][r['id']])!=r['poseTransformSha256']:continue
    score=(int(not r['geometricPassed']),r['skinAndClothSelfCrossingPairs'],r['guitar'].get('crossingPairs',99999),sum(not t['passed']for t in r['contacts']))
    if r['id']not in best or score<best[r['id']][0]:best[r['id']]=(score,lib['poses'][r['id']],p,r)
  except Exception:continue
 return best

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--chords',required=True);ap.add_argument('--out',type=Path,required=True);ap.add_argument('--seconds',type=int,default=100);ap.add_argument('--rounds',type=int,default=3);args=ap.parse_args();args.out=args.out.resolve();context=f.load_context();base=copy.deepcopy(context['library']);best=best_seeds();args.out.mkdir(parents=True,exist_ok=True)
 for key in args.chords.split(','):
  folder=args.out/key;folder.mkdir(exist_ok=True)
  if(folder/'result.json').exists():
   prior=json.loads((folder/'result.json').read_text())
   if not prior.get('error'):print('RESUME-complete',key,flush=True);continue
   (folder/'result.json').rename(folder/'result-initial-path-error.json')
  started=time.monotonic();history=[]
  try:
   assert key not in context['accepted'],'Preserve the original 13 exactly'
   if key in best:
    _,candidate,report_path,row=best[key];evidence=report_path.parent/row['rawEvidence'];seed_report=report_path
   else:
    candidate=f.previous.choose_seed(context,context['chords'][key])[0];candidate['chordId']=key;row=None;evidence=None;seed_report=None
   (folder/'seed.json').write_text(json.dumps(candidate,indent=2)+'\n');(folder/'seed-source.json').write_text(json.dumps({'source':str(seed_report),'transformSHA256':f.gate.transform_hash(candidate),'inputIsOnlyASeed':True},indent=2)+'\n')
   print('BEGIN',key,'bestKnown='+str(best.get(key,(None,))[0]),flush=True)
   chord=context['chords'][key]
   if row and row['maximumWoodDepthMm']>.02 and row['skinAndClothSelfCrossingPairs']==0:
    candidate=json.loads((folder/'thumb/candidate.json').read_text()) if (folder/'thumb/candidate.json').exists() else thumb.relax(candidate,folder/'thumb');report,file=(json.loads((folder/'thumb/audit/summary.json').read_text()),folder/'thumb/proposal-library.json') if (folder/'thumb/audit/summary.json').exists() else audit(base,candidate,folder/'thumb');row=report['rows'][0];evidence=file.parent/'audit'/row['rawEvidence'];history.append({'kind':'thumb-only','row':row,'report':str((file.parent/'audit/summary.json').relative_to(ROOT))});print('THUMB',key,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'passed',row['geometricPassed'],flush=True)
   for i in range(args.rounds):
    if row and row['geometricPassed']:break
    trial=folder/('round-'+str(i));exact=bool(i and row and row['skinAndClothSelfCrossingPairs']==0)
    if (trial/'candidate.json').exists() and (trial/'metrics.json').exists():candidate=json.loads((trial/'candidate.json').read_text());metrics=json.loads((trial/'metrics.json').read_text())
    else:candidate,metrics=f.fit(context,chord,candidate,trial,iterations=130,yaw=0,root_free=True,evidence=evidence,radius=None if i==0 else 14,exact_polish=exact,max_seconds=args.seconds,all_fingers=True,full_polish=True)
    report,file=(json.loads((trial/'audit/summary.json').read_text()),trial/'proposal-library.json') if (trial/'audit/summary.json').exists() else audit(base,candidate,trial);assert report['rows'][0]['poseTransformSha256']==f.gate.transform_hash(candidate); row=report['rows'][0];evidence=file.parent/'audit'/row['rawEvidence'];history.append({'kind':'all-five-digits','round':i,'metrics':metrics,'row':row,'report':str((file.parent/'audit/summary.json').relative_to(ROOT))});print('AUDIT',key,'round',i,'self',row['skinAndClothSelfCrossingPairs'],'guitar',row['guitar'].get('crossingPairs'),'contacts',sum(t['passed']for t in row['contacts']),'/',len(row['contacts']),'passed',row['geometricPassed'],flush=True)
   selected,decisions=f.previous.select_audited_replacements(base,json.loads(file.read_text()),report,sha(file),context['model_sha'],context['chord_sha'],[key]);result={'id':key,'selected':decisions[0]['selected'],'teachingApproved':False,'seconds':time.monotonic()-started,'history':history,'proposalFile':str(file.relative_to(ROOT)),'auditReport':str((file.parent/'audit/summary.json').relative_to(ROOT))}
   if result['selected']:(folder/'selected.json').write_text(json.dumps(selected['poses'][key],ensure_ascii=False,indent=2)+'\n')
  except Exception:result={'id':key,'selected':False,'error':traceback.format_exc(),'history':history};print('ERROR',key,result['error'],flush=True)
  (folder/'result.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');print('RESULT',key,result['selected'],flush=True)
if __name__=='__main__':main()
