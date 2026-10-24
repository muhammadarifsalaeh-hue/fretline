import os
"""Offline numeric native Blender rig -> original GLB joint-local matrix transfer.
No app adoption or pose/collision approval implied. Matrices serialize column-major.
"""
import json,struct,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
P=Path(os.environ.get('FRETLINE_STAGE3_DIR', '/tmp/fretline-stage3-assets'))
src=json.loads((P/'fk-source.json').read_text());pose=json.loads((P/'c-pose-offset-attempt-0.json').read_text());blob=(P/'anatomical-hand-optimized.glb').read_bytes()
lj,tj=struct.unpack_from('<II',blob,12);g=json.loads(blob[20:20+lj]);lb,tb=struct.unpack_from('<II',blob,20+lj);binary=blob[28+lj:28+lj+lb]
def access(ai):
 a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];dt={5126:np.dtype('<f4'),5123:np.dtype('<u2'),5121:np.dtype('u1')}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];stride=v.get('byteStride',n*dt.itemsize);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
 out=np.ndarray((a['count'],n),dtype=dt,buffer=binary,offset=offset,strides=(stride,dt.itemsize)).copy()
 if a.get('normalized'):out=out.astype(float)/np.iinfo(dt).max
 return out.astype(float)
C=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1]],float);Ci=np.linalg.inv(C)
names=[b['name'] for b in src['bones']];rest=np.array([b['matrix'] for b in src['bones']]);inverse=np.linalg.inv(rest);parents=[names.index(b['parent']) if b['parent'] else -1 for b in src['bones']];posed=np.empty_like(rest)
for i,p in enumerate(parents):
 rel=inverse[p]@rest[i] if p>=0 else rest[i];basis=np.eye(4);basis[:3,:3]=Rotation.from_euler('xyz',pose['angles'][names[i]]).as_matrix();posed[i]=(posed[p]@rel if p>=0 else rel)@basis
nativeDeform=posed@inverse;skin=g['skins'][0];ibm=access(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1);nodeParents={c:i for i,n in enumerate(g['nodes']) for c in n.get('children',[])};wanted={}
for ji,ni in enumerate(skin['joints']):
 bi=names.index(g['nodes'][ni]['name']);deform=C@nativeDeform[bi]@Ci;wanted[ni]=deform@np.linalg.inv(ibm[ji])
locals={ni:np.linalg.inv(wanted[nodeParents[ni]])@mat if nodeParents.get(ni) in wanted else mat.copy() for ni,mat in wanted.items()}
# Reconstruct from emitted local matrices using hierarchy, as Three.Object3D does.
reconstructed={}
def world(ni):
 if ni in reconstructed:return reconstructed[ni]
 p=nodeParents.get(ni);reconstructed[ni]=(world(p) if p in locals else np.eye(4))@locals[ni];return reconstructed[ni]
joints=np.array([world(ni) for ni in skin['joints']]);glbSkin=joints@ibm
q=np.array(pose['q']);outer=np.eye(4);outer[:3,:3]=Rotation.from_euler('xyz',q[:3]).as_matrix()@np.diag([-1,1,1])*q[6];outer[:3,3]=q[3:6];mmFromGLTF=outer@Ci
reports=[]
for node in [n for n in g['nodes'] if 'mesh' in n]:
 primitive=g['meshes'][node['mesh']]['primitives'][0];attr=primitive['attributes'];v=access(attr['POSITION']);j=access(attr['JOINTS_0']).astype(int);w=access(attr['WEIGHTS_0']);vh=np.column_stack((v,np.ones(len(v))));mat=(glbSkin[j]*w[:,:,None,None]).sum(1);glbposed=np.einsum('vij,vj->vi',mat,vh)@mmFromGLTF.T
 native=next(m for m in src['meshes'] if m['name']==node['name']);nv=np.array([v['co'] for v in native['verts']]);nw=np.array([v['weights'] for v in native['verts']]);nvh=np.column_stack((nv,np.ones(len(nv))));dist,mapping=cKDTree((nvh@C.T)[:,:3]).query(v)
 nmat=np.einsum('vb,bij->vij',nw,nativeDeform);nativeposed=np.einsum('vij,vj->vi',nmat,nvh)@outer.T;expected=nativeposed[mapping];err=np.linalg.norm(glbposed[:,:3]-expected[:,:3],axis=1)
 gw=np.zeros((len(v),len(names)))
 for col in range(4):
  for row in range(len(v)):gw[row,names.index(g['nodes'][skin['joints'][j[row,col]]]['name'])]+=w[row,col]
 wd=np.abs(gw-nw[mapping]);report={'mesh':node['name'],'gltfVertices':len(v),'nativeVertices':len(nv),'restMappingMaxSourceUnits':float(dist.max()),'restMappingMaxMm':float(dist.max()*q[6]),'nativeMaxNonzeroInfluences':int((nw>1e-8).sum(1).max()),'top4WeightL1Max':float(wd.sum(1).max()),'top4WeightElementMax':float(wd.max()),'poseErrorMaxMm':float(err.max()),'poseErrorMeanMm':float(err.mean()),'verticesAbovePoint1Mm':int((err>.1).sum())};reports.append(report)
 np.savez_compressed(P/(node['name'].lower()+'-runtime-transfer-points.npz'),gltfRest=v,gltfPosedMM=glbposed[:,:3],nativeMap=mapping,nativePosedMM=expected[:,:3],triangles=access(primitive['indices']).astype(int).reshape(-1,3))
passed=all(r['poseErrorMaxMm']<.1 and r['restMappingMaxMm']<.001 for r in reports)
report={'status':'PASS numerical transfer only' if passed else 'FAIL numerical transfer','poseSource':'c-pose-offset-attempt-0.json','modelSha256':hashlib.sha256(blob).hexdigest(),'nativeToGLTFAxes':'[x,z,-y]','matrixStorage':'column-major, assign with Matrix4.fromArray; matrixAutoUpdate=false','maxHierarchyReconstructionError':float(np.max(np.abs(joints-np.array([wanted[n] for n in skin['joints']])))),'meshes':reports,'scopeLimitations':['Does not validate playable C pose, collisions, anatomy, or teaching correctness.','Does not validate actual WebGL skinning, PBR textures, camera, or browser performance.','GlobalmmFromGLTF includes a reflection to make left hand; runtime must handle reflected winding.','Original GLB armature constraints absent; all pose matrices explicitly baked from bounded native pose.']}
(P/'runtime-transfer-audit.json').write_text(json.dumps(report,indent=2))
if passed:
 out={'status':'Numerically transferred experimental pose; NOT collision-approved or adopted into app','chord':'C','poseSource':'c-pose-offset-attempt-0.json','modelSha256':report['modelSha256'],'units':'millimetres before final study scene scale','matrixStorage':'column-major','mmFromGLTF':mmFromGLTF.T.reshape(-1).tolist(),'jointLocals':{g['nodes'][ni]['name']:mat.T.reshape(-1).tolist() for ni,mat in locals.items()},'pressOffsetsMm':pose['pressOffsetsBeforeWireMM'],'license':'CC BY-NC 4.0; copyright Emma L. D. Lieker; source attribution and modification notice required'};(P/'c-major-runtime-pose.json').write_text(json.dumps(out,indent=2))
print(json.dumps(report,indent=2))
