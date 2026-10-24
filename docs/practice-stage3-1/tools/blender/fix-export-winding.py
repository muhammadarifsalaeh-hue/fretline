"""Repair known canonical-mm Blender mirrored-armature GLB winding, not hand geometry/pose.
Authored NORMAL is checked first. Never flips NORMAL, position, weight, or bone data.
Current C remains unapproved. A positive winding test is not a collision/teaching gate.
"""
import argparse,json,struct,hashlib,sys
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'audit'))
from skin_from_glb import evaluate


def signs(mesh):
    v=mesh['positions'];t=mesh['triangles'];normal=np.cross(v[t[:,1]]-v[t[:,0]],v[t[:,2]]-v[t[:,0]]);normal/=np.maximum(np.linalg.norm(normal,axis=1)[:,None],1e-20);auth=mesh['authoredNormalsWorld'][t].mean(1);auth/=np.maximum(np.linalg.norm(auth,axis=1)[:,None],1e-20);dots=np.einsum('ij,ij->i',normal,auth);return {'medianGeometricDotAuthored':float(np.median(dots)),'meanGeometricDotAuthored':float(dots.mean()),'minGeometricDotAuthored':float(dots.min())}


def sha(x):return hashlib.sha256(x).hexdigest()


def run(a):
    assert a.input.resolve()!=a.output.resolve(),'Never overwrite Blender original export'
    before,meta=evaluate(a.input,None,None,False,True)
    raw=a.input.read_bytes();jl,jt=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+jl]);bl,bt=struct.unpack_from('<II',raw,20+jl);binary=bytearray(raw[28+jl:28+jl+bl]);originalbin=bytes(binary);rows=[];done=set();changed=[]
    for ni,node in enumerate(g['nodes']):
        if 'mesh'not in node:continue
        for pi,primitive in enumerate(g['meshes'][node['mesh']]['primitives']):
            if primitive.get('mode',4)!=4:raise ValueError('Only triangle primitives supported')
            name=node.get('name',f'mesh-{ni}')+(f'-{pi}'if pi else'');mesh=before[name]
            if mesh['authoredNormalsWorld']is None:raise ValueError('Authored NORMAL required for explicit winding verification')
            check=signs(mesh);median=check['medianGeometricDotAuthored'];row={'mesh':name,'before':check,'indicesFlipped':False}
            if median<-.75:
                ai=primitive.get('indices');assert ai is not None,'Indexed export required';acc=g['accessors'][ai];view=g['bufferViews'][acc['bufferView']];dt=np.dtype({5121:'u1',5123:'<u2',5125:'<u4'}[acc['componentType']]);stride=view.get('byteStride',dt.itemsize);offset=view.get('byteOffset',0)+acc.get('byteOffset',0);assert acc['count']%3==0
                if ai not in done:
                    indices=np.ndarray((acc['count'],),dtype=dt,buffer=binary,offset=offset,strides=(stride,));ii=indices.reshape(-1,3).copy();ii[:,[1,2]]=ii[:,[2,1]];indices[:]=ii.ravel();done.add(ai);changed.append(ai)
                row['indicesFlipped']=True
            elif median<.75:raise ValueError(f'Ambiguous winding/normal evidence for{name}: {median}; requires manual inspection')
            rows.append(row)
    # No geometry attributes are modified; annotate only asset extras and index bytes.
    g.setdefault('asset',{}).setdefault('extras',{})['fretlineCanonicalWindingRepair']={'method':'Known mirrored-armature canonical-mm export; swap index1/2 where geometric normals oppose authored outward NORMAL','sourceSHA256':sha(raw),'indexAccessorsChanged':changed,'poseApproved':False,'nonIndexBufferDataUnchanged':True}
    encoded=json.dumps(g,separators=(',',':')).encode();encoded+=b' '*((-len(encoded))%4);bb=bytes(binary);bb+=b'\0'*((-len(bb))%4);out=struct.pack('<III',0x46546c67,2,12+8+len(encoded)+8+len(bb))+struct.pack('<II',len(encoded),0x4e4f534a)+encoded+struct.pack('<II',len(bb),0x004e4942)+bb;a.output.write_bytes(out)
    after,post=evaluate(a.output,None,None,False,True)
    for row in rows:
        name=row['mesh'];b,c=before[name],after[name];row['after']=signs(c);row['positionsByteNumericallyIdentical']=bool(np.array_equal(b['positions'],c['positions']));row['authoredNormalsNumericallyIdentical']=bool(np.array_equal(b['authoredNormalsWorld'],c['authoredNormalsWorld']));assert row['positionsByteNumericallyIdentical']and row['authoredNormalsNumericallyIdentical'];assert row['after']['medianGeometricDotAuthored']>.75
    # All bytes outside changed index accessors must remain identical, including bones/weights/textures.
    expected=bytearray(originalbin)
    for ai in changed:
        acc=g['accessors'][ai];view=g['bufferViews'][acc['bufferView']];size={5121:1,5123:2,5125:4}[acc['componentType']];offset=view.get('byteOffset',0)+acc.get('byteOffset',0);stride=view.get('byteStride',size)
        for i in range(acc['count']):expected[offset+i*stride:offset+i*stride+size]=binary[offset+i*stride:offset+i*stride+size]
    assert bytes(expected)==bytes(binary),'Unexpected non-index mutation'
    report={'status':'PASS winding correction only; C pose remainsFAILED/UNAPPROVED','input':str(a.input),'output':str(a.output),'inputSHA256':sha(raw),'outputSHA256':sha(out),'meshRows':rows,'indexAccessorsChanged':changed,'allNonIndexBinaryBytesIdentical':True,'geometryPositionNormalsWeightsBonesTexturesUntouched':True,'limitations':['Tests global mirrored-export winding against authored outward normals, not anatomical pose or collision freedom.','Before/after NORMAL alignment is a robust global orientation check; self-intersections can still have local invalid surface folds.','Known canonical-mm Blender hand export pipeline only; do not assume arbitrary glTF assets use this coordinate convention.']}
    a.report.write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2));return report


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--input',required=True,type=Path);p.add_argument('--output',required=True,type=Path);p.add_argument('--report',required=True,type=Path);run(p.parse_args())
