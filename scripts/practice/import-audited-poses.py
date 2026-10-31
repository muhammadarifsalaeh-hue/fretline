#!/usr/bin/env python3
"""Import only independently audited hand endpoints. No catalog/database writes."""
import argparse, copy, hashlib, importlib.util, json, shutil, subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('old',ROOT/'scripts/practice/final_solver/solve.py')
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
BASE='218eab5a1b72125b7981b01ebe8aa417dd58fef7'
LIB='src/features/practice/assets/hand-poses.json'
OUT=ROOT/'docs/practice-fingering-polish'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    baseline=json.loads(subprocess.check_output(['git','show',BASE+':'+LIB],cwd=ROOT))
    original={key for key,p in baseline['poses'].items() if p['audit']['collisionPassed'] and p['audit']['contactPassed']}
    model=sha(ROOT/'src/features/practice/assets/makehuman-left-arm-sleeved.glb');chords=sha(ROOT/'src/features/practice/data/chords.js')
    selected={};attempts=[];result=copy.deepcopy(baseline)
    # Reuse committed evidence first, so a fresh clone retains every completed
    # endpoint even when earlier local authoring folders are unavailable.
    inputs=sorted((OUT/'accepted').glob('*/result.json'))+sorted((ROOT/'.local-preview/practice-fingering/batches').glob('*/*/result.json'))
    for file in inputs:
        data=json.loads(file.read_text());key=data['id'];attempts.append(data)
        if not data.get('selected') or key in selected or key in original:continue
        proposal_file=ROOT/data['proposalFile'];report_file=ROOT/data['auditReport']
        proposal=json.loads(proposal_file.read_text());report=json.loads(report_file.read_text())
        imported,decisions=old.select_audited_replacements(baseline,proposal,report,sha(proposal_file),model,chords,[key])
        assert decisions[0]['selected'] is True
        candidate=imported['poses'][key];result['poses'][key]=candidate
        target=OUT/'accepted'/key;target.mkdir(parents=True,exist_ok=True)
        # Keep exact proposal bytes, source/asset/chord fingerprints and raw
        # independent collision evidence with each imported record.
        for source,destination in [(proposal_file,target/'proposal-library.json'),(report_file,target/'summary.json'),(report_file.parent/report['rows'][0]['rawEvidence'],target/report['rows'][0]['rawEvidence'])]:
            if source.resolve()!=destination.resolve():shutil.copyfile(source,destination)
        (target/'selected.json').write_text(json.dumps(candidate,ensure_ascii=False,indent=2)+'\n')
        (target/'result.json').write_text(json.dumps({'id':key,'selected':True,'teachingApproved':False,'proposalFile':str((target/'proposal-library.json').relative_to(ROOT)),'auditReport':str((target/'summary.json').relative_to(ROOT))},indent=2)+'\n')
        selected[key]={'id':key,'proposalSHA256':sha(proposal_file),'sourceReport':data['auditReport'],'transformSHA256':old.transform_hash(candidate),'teachingApproved':False}
    assert all(result['poses'][key]==baseline['poses'][key] for key in original)
    assert set(result['poses'])==set(baseline['poses']) and len(result['poses'])==42
    assert {k:v for k,v in result.items() if k!='poses'}=={k:v for k,v in baseline.items() if k!='poses'}
    current=json.loads((ROOT/LIB).read_text())
    # Refuse to overwrite unrelated or unapproved local pose edits.
    assert all(current['poses'][key] in (baseline['poses'][key],result['poses'][key]) for key in baseline['poses'])
    ledger={'baselineCommit':BASE,'modelSHA256':model,'sourceChordSHA256':chords,'originalAccepted':sorted(original),'newAccepted':list(selected.values()),'attempts':attempts,'runtimeWritten':args.write,'noAnatomicalCertification':True}
    OUT.mkdir(parents=True,exist_ok=True);(OUT/'import-ledger.json').write_text(json.dumps(ledger,ensure_ascii=False,indent=2)+'\n')
    if args.write:(ROOT/LIB).write_text(old.frozen_json(result))
    print(json.dumps({'original':len(original),'new':len(selected),'totalGeometry':len(original)+len(selected),'teachingApproved':0,'written':args.write}))
if __name__=='__main__':main()
