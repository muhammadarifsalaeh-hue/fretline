#!/usr/bin/env python3
"""Tiny review-only bone refinements against actual skinned triangle surfaces.

This is an authoring tool, not a verification gate. Exact runtime guitar and
self-crossing audits plus independent four-view inspection remain required.
"""
import argparse, importlib.util, json
from pathlib import Path
import numpy as np
from scipy.optimize import least_squares

ROOT=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('solver',ROOT/'scripts/practice/solve-hand-poses.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)

def segment_triangle_distances(tri,a,b):
    """Euclidean distance between a closed segment and each triangle."""
    # Interior edge/edge minima, plus their four boundary minima.
    direction=b-a; dd=direction@direction
    best=np.full(len(tri),np.inf)
    for i in range(3):
        start=tri[:,i];edge=tri[:,(i+1)%3]-start;w=start-a
        ee=np.einsum('ij,ij->i',edge,edge)
        de=edge@direction;ew=np.einsum('ij,ij->i',edge,w);dw=w@direction
        determinant=ee*dd-de*de
        s=np.divide(de*dw-dd*ew,determinant,out=np.zeros(len(tri)),where=determinant>1e-16)
        t=np.divide(ee*dw-de*ew,determinant,out=np.zeros(len(tri)),where=determinant>1e-16)
        separation=start+s[:,None]*edge-(a+t[:,None]*direction)
        interior=(determinant>1e-16)&(s>=0)&(s<=1)&(t>=0)&(t<=1)
        best=np.minimum(best,np.where(interior,np.linalg.norm(separation,axis=1),np.inf))
        for endpoint in (start,start+edge):
            v=np.clip((endpoint-a)@direction/dd,0,1)
            best=np.minimum(best,np.linalg.norm(endpoint-(a+v[:,None]*direction),axis=1))
        for endpoint in (a,b):
            v=np.clip(np.divide(np.einsum('ij,ij->i',endpoint-start,edge),ee,out=np.zeros(len(tri)),where=ee>1e-16),0,1)
            best=np.minimum(best,np.linalg.norm(start+v[:,None]*edge-endpoint,axis=1))
    u=tri[:,1]-tri[:,0];v=tri[:,2]-tri[:,0]
    normal=np.cross(u,v);normal_length=np.linalg.norm(normal,axis=1)
    normal=np.divide(normal,normal_length[:,None],out=np.zeros_like(normal),where=normal_length[:,None]>1e-16)
    uu=np.einsum('ij,ij->i',u,u);uv=np.einsum('ij,ij->i',u,v);vv=np.einsum('ij,ij->i',v,v);det=uu*vv-uv*uv
    def bary_inside(points):
        w=points-tri[:,0];uw=np.einsum('ij,ij->i',u,w);vw=np.einsum('ij,ij->i',v,w)
        s=np.divide(vv*uw-uv*vw,det,out=np.zeros(len(tri)),where=det>1e-16)
        t=np.divide(uu*vw-uv*uw,det,out=np.zeros(len(tri)),where=det>1e-16)
        return (det>1e-16)&(s>=0)&(t>=0)&(s+t<=1)
    for endpoint in (a,b):
        height=np.einsum('ij,ij->i',endpoint-tri[:,0],normal)
        projected=endpoint-height[:,None]*normal
        best=np.minimum(best,np.where(bary_inside(projected),abs(height),np.inf))
    denominator=normal@direction
    parameter=np.divide(np.einsum('ij,ij->i',tri[:,0]-a,normal),denominator,out=np.zeros(len(tri)),where=abs(denominator)>1e-16)
    hit=a+parameter[:,None]*direction
    crossings=(abs(denominator)>1e-16)&(parameter>=0)&(parameter<=1)&bary_inside(hit)
    return np.where(crossings,0,best)

def line_clearance(tri,line,radius):
    return min(float(segment_triangle_distances(tri,a,b).min()) for a,b in zip(line[:-1],line[1:]))-radius

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',default=str(Path(__file__).with_name('C-palmar-relaxed.json')))
    ap.add_argument('--output',default=str(Path(__file__).with_name('C-contact-refined.json')))
    args=ap.parse_args();r=m.Rig(ROOT/'docs/practice-trainer/models/authoring/rig-data.json')
    seed=json.load(open(args.input));params=np.array(seed['solverParameters']);targets=m.c_targets();summary=[]
    for fi,target in enumerate(targets):
        finger=target['finger'];i=m.FINGERS.index(finger);slot=slice(6+4*i,10+4*i)
        original=params[slot].copy();world,*_=r.fk(params);points=r.skin(world)
        cap_start=points[r.patch_ids[finger]].mean(0)
        line=m.string_polyline(target['string'],targets);radius=m.GAUGES[target['string']-1]/2
        before=line_clearance(points[r.finger_triangles[finger]],line,radius)
        def lift_residual(angles):
            current=params.copy();current[slot]=angles;world,*_=r.fk(current);points=r.skin(world)
            cap=points[r.patch_ids[finger]].mean(0)
            hit=r.lower_surface(points,finger,target['positionMm'][0],target['positionMm'][2])
            lower=hit['positionMm'][1] if hit else cap[1]
            return np.r_[(cap[[0,2]]-cap_start[[0,2]])*.6,(lower-target['positionMm'][1]-.6)*20,(angles-original)*.08]
        # A line crossing a triangle has a flat unsigned-distance zero. First
        # lift its lower flesh surface out of that interior, then fit contact.
        lifted=least_squares(lift_residual,original,bounds=(original-np.deg2rad(6),original+np.deg2rad(6)),max_nfev=45,ftol=1e-9,xtol=1e-9,gtol=1e-9)
        def residual(angles):
            current=params.copy();current[slot]=angles;world,*_=r.fk(current);points=r.skin(world)
            cap=points[r.patch_ids[finger]].mean(0)
            clearance=line_clearance(points[r.finger_triangles[finger]],line,radius)
            return np.r_[(cap[[0,2]]-cap_start[[0,2]])*.6,(clearance-.008)*20,(angles-original)*.08]
        result=least_squares(residual,lifted.x,bounds=(original-np.deg2rad(6),original+np.deg2rad(6)),max_nfev=70,ftol=1e-10,xtol=1e-10,gtol=1e-10,diff_step=1e-5)
        params[slot]=result.x;world,*_=r.fk(params);points=r.skin(world)
        after=line_clearance(points[r.finger_triangles[finger]],line,radius)
        summary.append({'finger':finger,'string':target['string'],'beforeClearanceMm':before,'afterClearanceMm':after,'angularChangeDegrees':np.rad2deg(result.x-original).tolist(),'evaluations':result.nfev})
        print(json.dumps(summary[-1]),flush=True)
    candidate=m.write_candidate(r,params,targets,args.output)
    candidate['audit']['metrics']['contactRefinement']=summary
    Path(args.output).write_text(json.dumps(candidate,indent=2)+'\n')
    print(json.dumps({'output':args.output,'wood':candidate['audit']['metrics']['allMeshWoodSamples']},indent=2))

if __name__=='__main__':main()
