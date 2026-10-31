#!/usr/bin/env python3
"""Conservative one-dimensional clearance polish; exact post-audit still required."""
import argparse,copy,importlib.util,json
from pathlib import Path
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('fitter',ROOT/'scripts/practice/fit-missing-poses.py')
fitter=importlib.util.module_from_spec(spec);spec.loader.exec_module(fitter)
gate=fitter.gate


def polish(context,chord,seed,folder,shifts=None):
    folder.mkdir(parents=True,exist_ok=True);r=context['rig'];guitar=fitter.previous.runtime_guitar(chord,folder)
    lines={s['number']:s for s in guitar['strings']};contacts=gate.contacts(chord);world=gate.a.world_from_pose(r,seed);base=r.skin(world);rows=[]
    selected=None
    for shift in shifts if shifts is not None else np.arange(0,.301,.01):
        points=base+np.array([0,float(shift),0]);whole={};owned=[]
        for number,s in lines.items():
            line=np.array(s['controlPointsMm']);whole[number]=gate.clearance(points[r.triangles],list(zip(line[:-1],line[1:])),s['radiusMm'])
        for contact in contacts:
            finger=fitter.m.FINGERS[contact['finger']-1];faces=context['faces'][finger,'barre' if contact['kind']=='barre' else 'tip'];s=lines[contact['string']];wire=fitter.m.fret_x(contact['fret'])
            value=gate.clearance(points[faces],gate.clip_line(np.array(s['controlPointsMm']),wire-6,wire-1.1),s['radiusMm'])
            owned.append(dict(contact,clearanceMm=value))
        passed=all(.002<=t['clearanceMm']<=.115 for t in owned) and all(value>=(.205 if chord['frets'][6-number]==0 else .002) for number,value in whole.items())
        rows.append({'liftMm':float(shift),'ownedContacts':owned,'wholeSkinStringClearances':whole,'clearancesPassed':passed})
        if passed:
            selected=copy.deepcopy(seed);selected['root']['positionMm'][1]+=float(shift)
            selected['audit']={k:False for k in fitter.previous.GATES};selected['status']='needs-review';selected['reviewed']=False
            selected['reason']={'th':'ท่าที่ปรับระยะสัมผัส ยังต้องผ่านการตรวจเมชจริง','en':'Clearance-polished candidate; exact mesh acceptance is still required.'}
            selected['authoringSource']={'method':'Exact whole-skin and owned-pad clearances, rigid Y translation only','seedTransformSHA256':gate.transform_hash(seed),'liftMm':float(shift),'modelSHA256':context['model_sha'],'chordDataSHA256':context['chord_sha']}
            (folder/'candidate.json').write_text(json.dumps(selected,ensure_ascii=False,indent=2)+'\n')
            break
    (folder/'clearance-scan.json').write_text(json.dumps({'chord':chord['id'],'selectedCandidate':selected is not None,'notAnAcceptanceGate':True,'samples':rows},indent=2)+'\n')
    return selected


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--chord',required=True);parser.add_argument('--seed-file',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();context=fitter.load_context();seed=json.loads(args.seed_file.read_text());selected=polish(context,context['chords'][args.chord],seed,args.output)
    if selected:
        proposal=copy.deepcopy(context['library']);proposal['poses'][args.chord]=selected;(args.output/'proposal-library.json').write_text(fitter.previous.frozen_json(proposal))
    print(json.dumps({'chord':args.chord,'candidateFound':selected is not None,'runtimeWritten':False}))

if __name__=='__main__':main()
