"""Decode actual exported GLB rest transforms/LBS buffers and surface landmarks."""
import json,struct,hashlib
from pathlib import Path
import numpy as np
from scipy.spatial.transform import Rotation
ROOT=Path(__file__).resolve().parents[4];ASSETS=ROOT/'src/features/practice/assets';FILE=ASSETS/'makehuman-left-arm-sleeved.glb';raw=FILE.read_bytes()
offset=12;g=None;blob=None
while offset<len(raw):
 length,kind=struct.unpack_from('<II',raw,offset);data=raw[offset+8:offset+8+length];offset+=8+length
 if kind==0x4e4f534a:g=json.loads(data)
 if kind==0x004e4942:blob=data
DT={5120:'i1',5121:'u1',5122:'<i2',5123:'<u2',5125:'<u4',5126:'<f4'};SIZE={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}
def acc(index):
 a=g['accessors'][index];v=g['bufferViews'][a['bufferView']];dtype=np.dtype(DT[a['componentType']]);n=SIZE[a['type']];start=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',n*dtype.itemsize)
 out=np.ndarray((a['count'],n),dtype=dtype,buffer=blob,offset=start,strides=(stride,dtype.itemsize)).copy()
 if a.get('normalized') and a['componentType']!=5126:out=out.astype(float)/np.iinfo(dtype).max
 return out
parents={child:i for i,n in enumerate(g['nodes']) for child in n.get('children',[])}
def local(n):
 if 'matrix' in n:return np.array(n['matrix']).reshape(4,4,order='F')
 mat=np.eye(4);mat[:3,:3]=Rotation.from_quat(n.get('rotation',[0,0,0,1])).as_matrix()@np.diag(n.get('scale',[1,1,1]));mat[:3,3]=n.get('translation',[0,0,0]);return mat
world={}
def worldmat(i):
 if i not in world:world[i]=(worldmat(parents[i]) if i in parents else np.eye(4))@local(g['nodes'][i])
 return world[i]
metadata=json.loads((ASSETS/'makehuman-left-arm.metadata.json').read_text());sourcebones={x['name']:x for x in metadata['bones']}
nodes=[]
for i,n in enumerate(g['nodes']):
 if n.get('name') not in sourcebones:continue
 nodes.append({'nodeIndex':i,'name':n['name'],'parentNodeIndex':parents.get(i),'parentName':g['nodes'][parents[i]].get('name') if i in parents else None,'translation':n.get('translation',[0,0,0]),'rotation':n.get('rotation',[0,0,0,1]),'scale':n.get('scale',[1,1,1]),'localMatrix':local(n).tolist(),'worldMatrix':worldmat(i).tolist(),'headWorldMeters':worldmat(i)[:3,3].tolist(),'tailWorldMeters':sourcebones[n['name']]['sourceRestTailMeters']})
result={'schemaVersion':2,'glb':str(FILE.relative_to(ROOT)),'sha256':hashlib.sha256(raw).hexdigest(),'assetBytes':len(raw),'units':'metres','millimetresPerAssetUnit':1000,'coordinateSystem':'glTF Y-up, original MakeHuman axes, no reflection; wrist.L head at origin','poseStatus':'unavailable','handPoseVerified':False,'boneRestData':nodes,'meshes':[]}
for ni,node in enumerate(g['nodes']):
 if 'mesh' not in node or 'skin' not in node:continue
 skin=g['skins'][node['skin']];skin_names=[g['nodes'][j]['name'] for j in skin['joints']];ibm=acc(skin['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1)
 for pi,primitive in enumerate(g['meshes'][node['mesh']]['primitives']):
  attrs={k:acc(v) for k,v in primitive['attributes'].items()};positions=attrs['POSITION'];weights=attrs['WEIGHTS_0'];joints=attrs['JOINTS_0'];normals=attrs['NORMAL'];indices=acc(primitive['indices']).reshape(-1)
  assert all(np.isfinite(a).all() for a in attrs.values()),node['name']
  assert np.isfinite(ibm).all() and np.isfinite(worldmat(ni)).all(),node['name']
  assert np.max(joints)<len(skin_names) and np.min(weights)>=0,node['name']
  assert np.allclose(weights.sum(axis=1),1,atol=2e-6),node['name']
  assert np.max(indices)<len(positions),node['name']
  normal_lengths=np.linalg.norm(normals,axis=1)
  assert np.allclose(normal_lengths,1,atol=2e-5),node['name']
  bind_error=max(float(np.max(np.abs(worldmat(j)@bind-worldmat(ni)))) for j,bind in zip(skin['joints'],ibm))
  assert bind_error<2e-6,(node['name'],bind_error)
  # glTF duplicates vertices along UV seams. Weld equal positions only for the
  # topology audit; leave every exported position/index/weight unchanged.
  _,weld=np.unique(np.round(positions,7),axis=0,return_inverse=True)
  graph=[set() for _ in range(int(weld.max())+1)]
  for triangle in indices.reshape(-1,3):
   a,b,c=(int(weld[v]) for v in triangle)
   for u,v in ((a,b),(b,c),(c,a)):graph[u].add(v);graph[v].add(u)
  unseen=set(range(len(graph)));components=[]
  while unseen:
   pending=[unseen.pop()];size=0
   while pending:
    v=pending.pop();size+=1
    for adjacent in graph[v]:
     if adjacent in unseen:unseen.remove(adjacent);pending.append(adjacent)
   components.append(size)
  audit={'allAttributesFinite':True,'unitNormals':True,'normalLengthRange':[float(normal_lengths.min()),float(normal_lengths.max())],'allWeightsNormalized':True,'weightSumRange':[float(weights.sum(axis=1).min()),float(weights.sum(axis=1).max())],'influenceCountRange':[int(np.count_nonzero(weights,axis=1).min()),int(np.count_nonzero(weights,axis=1).max())],'skinJointCount':len(skin_names),'maxInverseBindRestError':bind_error,'boundsMeters':{'min':positions.min(0).tolist(),'max':positions.max(0).tolist()},'weldedVertexCount':len(graph),'weldedConnectedComponentSizes':sorted(components,reverse=True),'attributeSha256':{k:hashlib.sha256(a.tobytes()).hexdigest() for k,a in attrs.items()}}
  data={'name':node['name'],'nodeIndex':ni,'primitive':pi,'materialIndex':primitive.get('material'),'meshNodeWorldMatrix':worldmat(ni).tolist(),'skinJointNodes':skin['joints'],'skinJointNames':skin_names,'inverseBindMatrices':ibm.tolist(),'positions':positions.tolist(),'normals':normals.tolist(),'joints':joints.tolist(),'weights':weights.tolist(),'indices':indices.tolist(),'uvs':attrs.get('TEXCOORD_0',np.empty((0,2))).tolist(),'vertexCount':len(positions),'triangleCount':len(indices)//3,'audit':audit}
  if 'Hand_Forearm' in node['name']:
   wp=(worldmat(ni)@np.column_stack([positions,np.ones(len(positions))]).T).T[:,:3]
   bones={n['name']:n for n in nodes};index=np.array(bones['finger2-1.L']['headWorldMeters']);pinky=np.array(bones['finger5-1.L']['headWorldMeters']);middle=np.array(bones['finger3-1.L']['headWorldMeters']);wrist=np.array(bones['wrist.L']['headWorldMeters']);palm=np.cross(pinky-index,middle-wrist);palm/=np.linalg.norm(palm)
   landmarks={}
   for name,chain in metadata['fingerChains'].items():
    distal=chain[-1];si=skin_names.index(distal);b=bones[distal];head=np.array(b['headWorldMeters']);tail=np.array(b['tailWorldMeters']);axis=tail-head;length=np.linalg.norm(axis);axis/=length
    influence=np.sum(np.where(joints==si,weights,0),axis=1);along=(wp-head)@axis;mask=(influence>.58)&(along>.48*length)&(along<1.38*length)
    candidates=np.where(mask)[0];assert len(candidates)>5,(name,len(candidates))
    side=(wp-tail)@palm;front=candidates[np.argsort(side[candidates])[-8:]];back=candidates[np.argsort(side[candidates])[:8]]
    tip=int(candidates[np.argmax(along[candidates])])
    landmarks[name]={'distalBone':distal,'boneHeadMeters':head.tolist(),'boneTailMeters':tail.tolist(),'mostDistalVertex':tip,'surfaceSidePositive':{'vertexIndices':front.tolist(),'centerMeters':wp[front].mean(0).tolist()},'surfaceSideNegative':{'vertexIndices':back.tolist(),'centerMeters':wp[back].mean(0).tolist()},'boneLocalPositivePatchMeters':(np.linalg.inv(np.array(b['worldMatrix']))@np.r_[wp[front].mean(0),1])[:3].tolist(),'boneLocalNegativePatchMeters':(np.linalg.inv(np.array(b['worldMatrix']))@np.r_[wp[back].mean(0),1])[:3].tolist()}
   for landmark in landmarks.values():
    landmark['palmarSurface']=landmark['surfaceSidePositive'];landmark['dorsalSurface']=landmark['surfaceSideNegative']
    landmark['boneLocalPalmarPatchMeters']=landmark['boneLocalPositivePatchMeters'];landmark['boneLocalDorsalPatchMeters']=landmark['boneLocalNegativePatchMeters']
   evidence={'normalDefinition':'normalize((littleMCP-indexMCP) cross (middleMCP-wrist))','surfaceSidePositive':'palmar distal surface','surfaceSideNegative':'dorsal distal surface','verification':'Textured native and exported-GLB views: opposite positive-forward-cross view shows fingernails; this negative-forward-cross view shows palm and finger pads.','reviewScript':'docs/practice-trainer/models/authoring/render_anatomy_review.py','reviewDateUtc':'2026-10-25','guitarContactVerified':False}
   data['fingerSurfaceLandmarks']=landmarks;data['palmReferenceNormal']=palm.tolist();data['anatomicalSurfaceReference']=evidence
   metadata['fingerSurfaceLandmarks']=landmarks;metadata['palmReferenceNormal']=palm.tolist();metadata['anatomicalSurfaceReference']=evidence
  result['meshes'].append(data)
metadata.update({'assetFile':FILE.name,'assetSha256':result['sha256'],'assetBytes':len(raw),'license':'CC0 body, rig, weights and skin; CC-BY sleeve (version unspecified by source)','componentLicenses':{'bodyRigWeights':'CC0-1.0','skinTexture':'CC0-1.0','sleeve':{'license':'CC-BY (version unspecified)','author':'Elvaerwyn','source':'http://www.makehumancommunity.org/node/1800'}},'provenanceDocument':'docs/practice-trainer/models/README.md','exportedMeshes':[{'name':m['name'],'vertices':m['vertexCount'],'triangles':m['triangleCount']} for m in result['meshes']]})
assert {n['name'] for n in nodes}==set(metadata['expectedBoneNames'])
target=ROOT/'docs/practice-trainer/models/authoring/rig-data.json';target.write_text(json.dumps(result,separators=(',',':'))+'\n');(ASSETS/'makehuman-left-arm.metadata.json').write_text(json.dumps(metadata,indent=2)+'\n')
summary={'schemaVersion':1,'asset':result['glb'],'assetSha256':result['sha256'],'assetBytes':len(raw),'boneCount':len(nodes),'boneNames':[n['name'] for n in nodes],'poseVerified':False,'anatomicalSurfaceReference':metadata['anatomicalSurfaceReference'],'palmReferenceNormal':metadata['palmReferenceNormal'],'meshes':[{k:m[k] for k in ('name','vertexCount','triangleCount','audit')} for m in result['meshes']]}
(target.parent/'model-audit.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'output':str(target),'bytes':target.stat().st_size,'meshes':[(m['name'],m['vertexCount'],m['triangleCount']) for m in result['meshes']],'bones':len(nodes)}))
