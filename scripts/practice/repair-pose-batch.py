#!/usr/bin/env python3
"""Author/audit missing endpoints in isolated folders; never writes runtime data."""
import argparse,copy,gzip,hashlib,importlib.util,json,subprocess,traceback
from pathlib import Path
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fitter',ROOT/'scripts/practice/fit-missing-poses.py')
fitter=importlib.util.module_from_spec(spec);spec.loader.exec_module(fitter)
old=fitter.previous
lift_spec=importlib.util.spec_from_file_location('lift',ROOT/'scripts/practice/lift-pose.py')
lift=importlib.util.module_from_spec(lift_spec);lift_spec.loader.exec_module(lift)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def atomic_json(path,data):
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');temporary.replace(path)


def seed_for(context,chord):
    wanted=old.gate.contacts(chord)
    def score(key):
        source=old.gate.contacts(context['chords'][key]);cost=0
        for finger in range(1,5):
            target=[t for t in wanted if t['finger']==finger];before=[t for t in source if t['finger']==finger]
            if target and {(t['string'],t['fret']) for t in target}=={(t['string'],t['fret']) for t in before}:
                cost-=40
            else:
                for t in target:
                    cost+=min([abs(t['string']-s['string'])*6+abs(t['fret']-s['fret'])*3 for s in before] or [14])
                if before and not target:cost+=8
        return cost,key
    key=min(context['accepted'],key=score)
    return copy.deepcopy(context['library']['poses'][key])


def yaw_for(chord):
    contacts=old.gate.contacts(chord)
    if chord['barres']:return 0
    if max(t['fret'] for t in contacts)-min(t['fret'] for t in contacts)>=2:return 0
    for t in contacts:
        same=[s for s in contacts if s['fret']==t['fret']]
        if len(same)>=2 and max(s['string'] for s in same)-min(s['string'] for s in same)<=2:return 70
    return 0


def audit(baseline,candidate,folder,key):
    proposal=copy.deepcopy(baseline);proposal['poses'][key]=candidate
    file=folder/'proposal-library.json';file.write_text(old.frozen_json(proposal))
    with (folder/'audit.log').open('w') as log:
        subprocess.run(['python',str(ROOT/'scripts/practice/check-hand-geometry.py'),'--library',str(file),'--chords',key,'--require','','--output',str(folder/'audit')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,check=True)
    report=json.loads((folder/'audit/summary.json').read_text())
    return file,proposal,report


def adopt_shared(context,baseline,shared):
    available={}
    for result in shared.rglob('result.json'):
        data=json.loads(result.read_text())
        if not isinstance(data,dict) or 'id' not in data:continue
        key=data['id']
        if not data.get('selected'):continue
        available[key]=data
        if key in context['accepted']:continue
        proposal_file=ROOT/data['proposalFile'];report_file=ROOT/data['auditReport']
        proposal=json.loads(proposal_file.read_text());report=json.loads(report_file.read_text())
        selected,decisions=old.select_audited_replacements(baseline,proposal,report,digest(proposal_file),context['model_sha'],context['chord_sha'],[key])
        assert decisions[0]['selected']
        context['library']['poses'][key]=selected['poses'][key];context['accepted'].add(key)
    return available


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--chords',required=True);parser.add_argument('--output',type=Path,required=True);parser.add_argument('--shared',type=Path,required=True);parser.add_argument('--iterations',type=int,default=90);parser.add_argument('--rounds',type=int,default=3);parser.add_argument('--seconds',type=int,default=120)
    parser.add_argument('--all-fingers',action='store_true');parser.add_argument('--full-polish',action='store_true')
    args=parser.parse_args();args.output=args.output.resolve();args.shared=args.shared.resolve();context=fitter.load_context();baseline=copy.deepcopy(context['library']);args.output.mkdir(parents=True,exist_ok=True);results=[]
    for key in args.chords.split(','):
        folder=args.output/key;folder.mkdir(parents=True,exist_ok=True)
        if (folder/'result.json').exists():
            results.append(json.loads((folder/'result.json').read_text()));continue
        try:
            available=adopt_shared(context,baseline,args.shared)
            if key in available:
                result=copy.deepcopy(available[key]);result['reusedExistingExactAudit']=True
                (folder/'selected.json').write_text(json.dumps(context['library']['poses'][key],ensure_ascii=False,indent=2)+'\n')
                atomic_json(folder/'result.json',result);results.append(result);print('REUSED',key,flush=True);continue
            chord=context['chords'][key];seed=seed_for(context,chord);yaw=yaw_for(chord)
            print('BEGIN',key,'seed='+seed['chordId'],'yaw='+str(yaw),flush=True)
            constraints={'kind':'authoring-constraints','assetSha256':context['model_sha'],'sourceAuditFiles':[],'self':{'pairs':[]},'guitar':{'pairs':[]}}
            self_seen=set();guitar_seen=set();history=[];evidence=None;candidate=seed;proposal_file=None;report=None
            for iteration in range(args.rounds+1):
                trial=folder/('round-'+str(iteration))
                polish=bool(iteration and history[-1]['exactRow']['skinAndClothSelfCrossingPairs']==0)
                # Resume completed authoring/audits without replacing evidence.
                if (trial/'candidate.json').exists() and (trial/'metrics.json').exists():
                    candidate=json.loads((trial/'candidate.json').read_text());metrics=json.loads((trial/'metrics.json').read_text())
                else:
                    candidate,metrics=fitter.fit(context,chord,candidate,trial,iterations=args.iterations,yaw=yaw if iteration==0 else 0,root_free=True,evidence=evidence,radius=(5 if polish else 10) if iteration else None,exact_polish=polish,max_seconds=args.seconds,all_fingers=args.all_fingers,full_polish=args.full_polish)
                scratch=trial/(key+'-guitar.json')
                export_sha=digest(scratch) if scratch.exists() else None
                if scratch.exists():scratch.unlink()
                if (trial/'audit/summary.json').exists():
                    proposal_file=trial/'proposal-library.json';proposal=json.loads(proposal_file.read_text());report=json.loads((trial/'audit/summary.json').read_text())
                    assert report['librarySnapshotSha256']==digest(proposal_file)
                    assert report['rows'][0]['poseTransformSha256']==old.gate.transform_hash(candidate)
                else:proposal_file,proposal,report=audit(baseline,candidate,trial,key)
                row=report['rows'][0];history.append({'round':iteration,'metrics':metrics,'runtimeGuitarSHA256':export_sha,'exactRow':row,'report':str((trial/'audit/summary.json').relative_to(ROOT))})
                print('AUDIT',key,'round='+str(iteration),'self='+str(row['skinAndClothSelfCrossingPairs']),'guitar='+str(row['guitar'].get('crossingPairs')),'passed='+str(row['geometricPassed']),flush=True)
                if row['geometricPassed']:break
                if row['skinAndClothSelfCrossingPairs']==0 and row['contacts'] and all(abs(t['actualOwnerPalmarSkinClearanceMm'])<.22 for t in row['contacts']):
                    lifted=lift.polish(context,chord,candidate,trial/'rigid-clearance',shifts=np.arange(.02,.241,.02))
                    scratch=trial/'rigid-clearance'/(key+'-guitar.json')
                    if scratch.exists():scratch.unlink()
                    if lifted is not None:
                        lift_file,lift_proposal,lift_report=audit(baseline,lifted,trial/'rigid-clearance',key)
                        lift_row=lift_report['rows'][0]
                        history.append({'round':str(iteration)+'-rigid-clearance','exactRow':lift_row,'report':str((lift_file.parent/'audit/summary.json').relative_to(ROOT))})
                        if lift_row['geometricPassed']:
                            candidate=lifted;proposal_file=lift_file;proposal=lift_proposal;report=lift_report;break
                raw_file=trial/'audit'/(key+'-raw.json.gz')
                with gzip.open(raw_file,'rt') as stream:raw=json.load(stream)
                constraints['sourceAuditFiles'].append({'path':str(raw_file.relative_to(ROOT)),'sha256':digest(raw_file),'poseTransformSHA256':raw['poseTransformSha256']})
                for kind,seen in [('self',self_seen),('guitar',guitar_seen)]:
                    for pair in raw.get(kind,{}).get('pairs',[]):
                        signature=tuple(tuple(sorted(values)) for values in pair['vertices'])
                        if signature in seen:continue
                        seen.add(signature);constraints[kind]['pairs'].append(pair)
                constraints['poseTransformSha256']=old.gate.transform_hash(candidate)
                evidence=trial/'authoring-constraints.json';evidence.write_text(json.dumps(constraints,separators=(',',':'))+'\n')
            selected,decisions=old.select_audited_replacements(baseline,proposal,report,digest(proposal_file),context['model_sha'],context['chord_sha'],[key])
            result={'id':key,'selected':decisions[0]['selected'],'teachingApproved':False,'modelSHA256':context['model_sha'],'chordDataSHA256':context['chord_sha'],'proposalFile':str(proposal_file.relative_to(ROOT)),'auditReport':str((proposal_file.parent/'audit/summary.json').relative_to(ROOT)),'history':history}
            if result['selected']:
                context['library']['poses'][key]=selected['poses'][key];context['accepted'].add(key)
                (folder/'selected.json').write_text(json.dumps(selected['poses'][key],ensure_ascii=False,indent=2)+'\n')
            print('RESULT',key,'SELECTED' if result['selected'] else 'REJECTED',flush=True)
        except Exception:
            result={'id':key,'selected':False,'error':traceback.format_exc()};print('ERROR',key,result['error'],flush=True)
        atomic_json(folder/'result.json',result);results.append(result)
        atomic_json(args.output/'progress.json',{'completed':len(results),'results':results,'runtimeWritten':False})

if __name__=='__main__':main()
