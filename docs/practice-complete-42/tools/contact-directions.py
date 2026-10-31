"""Actual closest skin/string pairs: diagnose whether pressure comes from above.
This supplements the original exact collision/contact gate; it never approves anatomy.
"""
import argparse,hashlib,importlib.util,json,subprocess,tempfile
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3]
s=importlib.util.spec_from_file_location('f',Path(__file__).with_name('fit-pressure-v4.py'));f=importlib.util.module_from_spec(s);s.loader.exec_module(f)
def measure(context,pose,folder):
 key=pose['chordId'];chord=context['chords'][key];r=context['rig'];file=folder/'pose.json';file.write_text(json.dumps(pose));guitar_file=folder/'guitar.json';subprocess.run(['node',str(Path(__file__).with_name('export-guitar.mjs')),key,str(guitar_file),str(file)],cwd=ROOT,check=True);guitar=json.loads(guitar_file.read_text());lines={line['number']:line for line in guitar['strings']};points=r.skin(f.a.world_from_pose(r,pose));rows=[]
 for target in (f.effective_contacts(chord)if 'pressOffsetsMm'in pose else f.gate.contacts(chord)):
  finger=f.m.FINGERS[target['finger']-1];faces=context['faces'][finger,'barre'if target['kind']=='barre'else'tip'];tri=points[faces];line=lines[target['string']];wire=f.m.fret_x(target['fret']);press=wire-pose['pressOffsetsMm'][f"{target['string']}:{target['fret']}"]if 'pressOffsetsMm'in pose else None;segments=f.gate.clip_line(np.array(line['controlPointsMm']),press-.5 if press is not None else wire-6,press+.5 if press is not None else wire-1.1);best=None
  for start,end in segments:
   distances=f.a.c.segment_triangle_distances(tri,start,end);index=int(np.argmin(distances));A,B,C=tri[index];D=end-start;E=B-A;F=C-A
   def objective(x):
    v=start+x[0]*D-A-x[1]*E-x[2]*F;return float(v@v)
   def jac(x):
    v=start+x[0]*D-A-x[1]*E-x[2]*F;return np.array([2*D@v,-2*E@v,-2*F@v])
   result=minimize(objective,[.5,.3,.3],jac=jac,method='SLSQP',bounds=[(0,1)]*3,constraints=[{'type':'ineq','fun':lambda x:1-x[1]-x[2],'jac':lambda x:np.array([0,-1,-1])}],options={'ftol':1e-14,'maxiter':120})
   t,u,v=result.x;center=start+t*D;skin=A+u*E+v*F;distance=float(np.linalg.norm(skin-center));assert abs(distance-distances[index])<1e-5,'Closest-point diagnostic disagrees with analytic exact clearance'
   if best is None or distance<best['distanceMm']:best={'distanceMm':distance,'centerlinePointMm':center.tolist(),'palmarSkinPointMm':skin.tolist(),'skinMinusCenterYmm':float(skin[1]-center[1]),'outwardFraction':float((skin[1]-center[1])/max(distance,1e-12)),'ownedTriangleVertexIndices':faces[index].tolist()}
  rows.append(dict(target,**best,pressureComesFromAbove=best['skinMinusCenterYmm']>0))
 return {'id':key,'poseTransformSHA256':f.gate.transform_hash(pose),'allPressedContactsFromAbove':all(t['pressureComesFromAbove']for t in rows),'contacts':rows,'teachingApproval':False}
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--pose',type=Path,required=True);ap.add_argument('--out',type=Path,required=True);args=ap.parse_args();context=f.load_context()
 with tempfile.TemporaryDirectory(prefix='fretline-contact-direction-')as temporary:report=measure(context,json.loads(args.pose.read_text()),Path(temporary))
 args.out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
