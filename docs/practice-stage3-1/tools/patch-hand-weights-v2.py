"""Joint-local repaint of the actual exported hand skin. Positions/UVs/topology unchanged.
Research candidate only, not an approved C pose. Source ©Emma L.D.Lieker CC BY-NC4.0.
"""
import json,struct,hashlib,copy
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
P=Path('/tmp/fretline-stage3-assets');O=Path('/tmp/fretline-stage31-assets');src=P/'anatomical-hand-optimized.glb';target=O/'anatomical-hand-weight-repaired-v2.glb';fk=json.loads((O/'weights-profile-mcp-linear-1.0-family0.8-nonthumb.json').read_text());originalfk=json.loads((P/'fk-source-gltf-compatible.json').read_text());raw=src.read_bytes();lj=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+lj]);lb=struct.unpack_from('<I',raw,20+lj)[0];binary=bytearray(raw[28+lj:28+lj+lb]);before=bytes(binary)
types={5126:np.dtype('<f4'),5123:np.dtype('<u2'),5121:np.dtype('u1')};components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def view(ai,data=binary):
 a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];dtype=types[a['componentType']];n=components[a['type']];return np.ndarray((a['count'],n),dtype=dtype,buffer=data,offset=v.get('byteOffset',0)+a.get('byteOffset',0),strides=(v.get('byteStride',n*dtype.itemsize),dtype.itemsize))
names=[b['name'] for b in fk['bones']];skin=g['skins'][0];joints=[names.index(g['nodes'][ni]['name']) for ni in skin['joints']];reverse={ni:i for i,ni in enumerate(joints)};C=np.array([[1,0,0],[0,0,1],[0,-1,0]],float)
node=next(n for n in g['nodes'] if n.get('name')=='Hand' and 'mesh' in n);p=g['meshes'][node['mesh']]['primitives'][0];attr=p['attributes'];v=view(attr['POSITION']).astype(float);mesh=next(m for m in fk['meshes'] if m['name']=='Hand');native=np.array([v['co'] for v in mesh['verts']]);dist,mapping=cKDTree(native@C.T).query(v);assert dist.max()<1e-7
w=np.array([v['weights'] for v in mesh['verts']]);originalw=np.array([v['weights'] for v in next(m for m in originalfk['meshes'] if m['name']=='Hand')['verts']]);assert np.allclose(w.sum(1),1);assert (w>1e-8).sum(1).max()<=4
jview=view(attr['JOINTS_0']);wview=view(attr['WEIGHTS_0']);assert g['accessors'][attr['WEIGHTS_0']]['componentType']==5126
for row,ni in enumerate(mapping):
 order=np.argsort(w[ni])[::-1][:4];jview[row]=[reverse[int(bi)] if w[ni,bi]>0 else 0 for bi in order];wview[row]=w[ni,order]
changedaccessors=[]
for ai in range(len(g['accessors'])):
 if not np.array_equal(view(ai,before),view(ai)) :changedaccessors.append(ai)
assert set(changedaccessors)<=set([attr['JOINTS_0'],attr['WEIGHTS_0']]),changedaccessors
# Assert every byte outside those two accessor spans is identical.
allowed=np.zeros(len(binary),dtype=bool)
for ai in [attr['JOINTS_0'],attr['WEIGHTS_0']]:
 a=g['accessors'][ai];bv=g['bufferViews'][a['bufferView']];start=bv.get('byteOffset',0)+a.get('byteOffset',0);element=types[a['componentType']].itemsize*components[a['type']];stride=bv.get('byteStride',element)
 for row in range(a['count']):allowed[start+row*stride:start+row*stride+element]=True
old=np.frombuffer(before,dtype=np.uint8);new=np.frombuffer(binary,dtype=np.uint8);assert np.array_equal(old[~allowed],new[~allowed])
changednative=int((np.abs(w-originalw).max(1)>1e-8).sum());changedgltf=int((np.abs(w[mapping]-originalw[mapping]).max(1)>1e-8).sum())
extra={'stage31WeightRepair':{'status':'unapproved research candidate; C pose must pass separate collision/teaching gate','method':'Nearest eligible finger MCP/PIP/DIP and thumb MCP/IP joint axial linear parent-child weights over plus/minus1.0 original sourceunit; restgeometry unchanged','changedNativeVertices':changednative,'changedGLTFVertices':changedgltf,'source':'https://github.com/emmalieker/anatomical-hand-model/tree/f27f19f55f8270b3108ea0b53ce5aa81c543ff7c','license':'CC BY-NC4.0; copyright2026Emma L.D.Lieker; attribution and modification notice required'}}
g.setdefault('asset',{}).setdefault('extras',{}).update(extra);js=json.dumps(g,separators=(',',':')).encode();js+=b' '*(-len(js)%4);binbytes=bytes(binary)+b'\0'*(-len(binary)%4);out=struct.pack('<III',0x46546C67,2,12+8+len(js)+8+len(binbytes))+struct.pack('<II',len(js),0x4E4F534A)+js+struct.pack('<II',len(binbytes),0x004E4942)+binbytes;target.write_bytes(out);(O/'fk-source-patched-v2.json').write_text(json.dumps(fk))
report={'status':'PASS weight-only patch integrity; NOT Cpose approval','source':str(src),'target':str(target),'sourceSHA256':hashlib.sha256(raw).hexdigest(),'targetSHA256':hashlib.sha256(out).hexdigest(),'bytes':len(out),'changedNativeVertices':changednative,'changedGLTFVertices':changedgltf,'maxInfluences':int((w>1e-8).sum(1).max()),'changedAccessors':changedaccessors,'allowedAccessors':[attr['JOINTS_0'],attr['WEIGHTS_0']],'allOtherAccessorBytesUnchanged':True,'allNonWeightJointBinaryBytesUnchanged':True,'restPositionNormalUVTopologyUnchanged':True,'nailsUnchanged':True,'maxRestMappingError':float(dist.max()),'poseNotApproved':True};(O/'weight-patch-v2-integrity.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
