"""Rebuild reproducible joint-local skin-weight repairs, without moving mesh vertices.

Input is the exact four-influence GLB representation on native topology.
Source geometry ©2026 Emma L.D.Lieker, CC BY-NC4.0. Research only; pose not approved.
"""
import json,copy,argparse
from pathlib import Path
import numpy as np

def repaint(source,stage):
    result=copy.deepcopy(source)
    mesh=next(m for m in result['meshes'] if m['name']=='Hand')
    bones=result['bones'];names=[b['name'] for b in bones]
    positions=np.array([v['co'] for v in mesh['verts']])
    baseline=np.array([v['weights'] for v in mesh['verts']])
    weights=baseline.copy()
    for vi,(v,w) in enumerate(zip(positions,baseline)):
        candidates=[]
        for bi,b in enumerate(bones):
            finger,_,part=b['name'].partition('_')
            if finger not in ['index','midd','ring','pinky','thumb']:continue
            if stage=='ip':
                if part not in ['prox','midd','dist']:continue
                if finger!='thumb' and part=='prox':continue
                radial_limit=1.25
            elif stage=='mcp':
                if finger=='thumb' or part!='prox':continue
                radial_limit=1.8
            else:raise ValueError(stage)
            family=[i for i,n in enumerate(names) if n.startswith(finger+'_')]
            if w[family].sum()<.8:continue
            matrix=np.array(b['matrix'])
            local=matrix[:3,:3].T@(v-np.array(b['head']))
            axial=local[1];radial=np.linalg.norm(local[[0,2]])
            if abs(axial)<1.0 and radial<radial_limit:
                candidates.append((np.linalg.norm(local),bi,axial))
        if candidates:
            _,bi,axial=min(candidates)
            parent=names.index(bones[bi]['parent'])
            fraction=np.clip((axial+1.0)/2.0,0,1)
            weights[vi]=0
            weights[vi,parent]=1-fraction
            weights[vi,bi]=fraction
    for v,w in zip(mesh['verts'],weights):v['weights']=w.tolist()
    assert np.allclose(weights.sum(1),1)
    assert (weights>1e-8).sum(1).max()<=4
    result['stage31WeightRepair']={'stage':stage,'poseApproved':False,
        'geometryUnchanged':True,'method':'joint-local axial linear parent/child ramp',
        'widthEachSideNative':1.0,'radialLimitNative':radial_limit,
        'minimumExistingFamilyWeight':.8,
        'changedHandNativeVerticesFromInput':int((np.max(np.abs(weights-baseline),axis=1)>1e-8).sum()),
        'sourceLicense':'CC BY-NC4.0; copyright2026Emma L.D.Lieker'}
    return result

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--input',type=Path,default=Path('/tmp/fretline-stage3-assets/fk-source-gltf-compatible.json'))
    parser.add_argument('--output',type=Path,default=Path('/tmp/fretline-stage31-assets'))
    args=parser.parse_args();args.output.mkdir(parents=True,exist_ok=True)
    source=json.loads(args.input.read_text());v1=repaint(source,'ip');v2=repaint(v1,'mcp')
    for label,variant in [('v1',v1),('v2',v2)]:
        (args.output/f'fk-source-rebuilt-{label}.json').write_text(json.dumps(variant))
    report={'status':'reproducible weight-only candidate; no pose approval','stages':[]}
    for label,variant,expected in [('v1',v1,args.output/'fk-source-patched.json'),('v2',v2,args.output/'fk-source-patched-v2.json')]:
        row={'stage':label,**variant['stage31WeightRepair']}
        if expected.exists():
            other=json.loads(expected.read_text())
            weights=np.array([v['weights'] for v in next(m for m in variant['meshes'] if m['name']=='Hand')['verts']])
            earlier=np.array([v['weights'] for v in next(m for m in other['meshes'] if m['name']=='Hand')['verts']])
            row['matchesEarlierExactWeights']=bool(np.array_equal(weights,earlier))
            assert row['matchesEarlierExactWeights']
        report['stages'].append(row)
    (args.output/'weight-repair-reproducibility.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
