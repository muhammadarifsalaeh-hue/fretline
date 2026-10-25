#!/usr/bin/env python3
"""Reproduce whole-skin string clearances and posed skin/garment mesh export."""
import argparse, hashlib, importlib.util, json
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
from scipy.spatial.transform import Rotation

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('contacts',HERE/'refine_c_contacts.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)

def world_from_pose(r, pose):
    """Actual authored runtime TRS is authoritative, not an IK seed vector."""
    local=r.rest_local.copy()
    for i,bone in enumerate(r.bones):
        local[i,:3,:3]=Rotation.from_quat(pose['bones'][bone['name']]['quaternion']).as_matrix()*np.array(bone['scale'])[None,:]
    world=np.zeros_like(local);done=set()
    def visit(i):
        if i in done:return
        parent=r.parents[i]
        if parent>=0:visit(parent);world[i]=world[parent]@local[i]
        else:world[i]=local[i]
        done.add(i)
    for i in range(len(r.bones)):visit(i)
    root=np.eye(4);root[:3,:3]=Rotation.from_quat(pose['root']['quaternion']).as_matrix()*1000
    root[:3,3]=pose['root']['positionMm']
    return root@world

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--candidate',default=str(HERE/'C-contact-refined.json'))
    ap.add_argument('--output',default=str(HERE/'C-contact-refined-clearances.json'))
    ap.add_argument('--combined-mesh',default='/tmp/fretline-trainer-pose/C-contact-refined-full-mesh.json')
    args=ap.parse_args();r=c.m.Rig(c.ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
    pose=json.loads(Path(args.candidate).read_text());world=world_from_pose(r,pose)
    # If a current solver vector exists, catch stale provenance; an authored
    # forearm/wrist variant intentionally has no current solverParameters.
    if 'solverParameters' in pose:
        solver_world,*_=r.fk(np.array(pose['solverParameters']))
        assert np.max(abs(world-solver_world))<1e-8,'Stale solverParameters do not reproduce actual authored TRS'
    points=r.skin(world);tri=points[r.triangles];out=[]
    for string in range(1,7):
        line=c.m.string_polyline(string,c.m.c_targets());minimum=(np.inf,None,None)
        for j,(a,b) in enumerate(zip(line[:-1],line[1:])):
            distances=c.segment_triangle_distances(tri,a,b);i=int(np.argmin(distances))
            if distances[i]<minimum[0]:minimum=(float(distances[i]),i,j)
        distance,i,j=minimum;a,b=line[j:j+2];A,B,C=tri[i];d=b-a;e=B-A;f=C-A
        def objective(x):
            separation=a+x[0]*d-A-x[1]*e-x[2]*f
            return separation@separation
        solved=minimize(objective,np.array([.1,.3,.3]),method='SLSQP',bounds=((0,1),(0,1),(0,1)),
            constraints=[{'type':'ineq','fun':lambda x:1-x[1]-x[2]}],options={'ftol':1e-15,'maxiter':150})
        t,u,v=solved.x;line_point=a+t*d;skin_point=A+u*e+v*f
        out.append({'string':string,'minimumWholeSkinTriangleClearanceMm':distance-c.m.GAUGES[string-1]/2,
            'triangle':i,'triangleVertexIndices':r.triangles[i].tolist(),'lineSegmentIndex':j,
            'linePointMm':line_point.tolist(),'skinPointMm':skin_point.tolist(),
            'closestPairCalculationConverged':bool(solved.success),'closestPairDistanceMm':float(np.linalg.norm(line_point-skin_point)),
            'barycentric':[float(1-u-v),float(u),float(v)]})
    transform={'root':pose['root'],'bones':pose['bones']}
    report={'assetSha256':pose['assetSha256'],'poseTransformSha256':hashlib.sha256(json.dumps(transform,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
        'transformSource':'Actual saved root quaternion/translation and all22 absoluteLOCALbonequaternions; rest translations/scales and original GLB skinweights; old sourceSolverParameters provenance is never used.',
        'scope':'All14760actualexportedGLBskintriangles vs physicalpiecewisecentrelines, circumcircleradiususedconservatively around6sidedactualtubes. Positiveclearanceprovesoutsidecircumscribedtube. SLSQPcoordinatesaresecondaryillustrativeclosestpointcalculation; authoritativeclearanceminimumcomesfromanalytictriangle/segmentdistance.','strings':out}
    Path(args.output).write_text(json.dumps(report,indent=2)+'\n')
    positions=[];indices=[];labels=[]
    for mesh in r.data['meshes']:
        vertices=r.skin_mesh(world,mesh);offset=len(positions);positions.extend(vertices.tolist())
        indices.extend((np.array(mesh['indices'])+offset).tolist());labels.extend([mesh['name']]*len(vertices))
    mesh_path=Path(args.combined_mesh);mesh_path.parent.mkdir(parents=True,exist_ok=True)
    mesh_path.write_text(json.dumps({'positions':positions,'indices':indices,'dominantBones':labels}))
    print(json.dumps({'output':args.output,'combinedMesh':str(mesh_path),'clearancesMm':[s['minimumWholeSkinTriangleClearanceMm'] for s in out]},indent=2))

if __name__=='__main__':main()
