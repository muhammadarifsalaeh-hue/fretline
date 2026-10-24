"""Actual GLB skin evaluation for isolated Fretline research. All output coordinates mm."""
import json, struct, hashlib
from pathlib import Path
import numpy as np


def euler_xyz(a):
    x,y,z=a;cx,sx=np.cos(x),np.sin(x);cy,sy=np.cos(y),np.sin(y);cz,sz=np.cos(z),np.sin(z)
    return np.array([[cz,-sz,0],[sz,cz,0],[0,0,1.]])@np.array([[cy,0,sy],[0,1,0],[-sy,0,cy]])@np.array([[1,0,0],[0,cx,-sx],[0,sx,cx]])


def trs(node):
    if 'matrix' in node:return np.array(node['matrix'],float).reshape(4,4).T
    x,y,z,w=node.get('rotation',[0,0,0,1]);q=np.array([x,y,z,w]);q=q/np.linalg.norm(q);x,y,z,w=q
    r=np.array([[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]])
    out=np.eye(4);out[:3,:3]=r@np.diag(node.get('scale',[1,1,1]));out[:3,3]=node.get('translation',[0,0,0]);return out


def evaluate(glb,pose_path=None,source_path=None,rest_control=False,baked_mm=False):
    raw=Path(glb).read_bytes();length,typ=struct.unpack_from('<II',raw,12);g=json.loads(raw[20:20+length]);blen,btyp=struct.unpack_from('<II',raw,20+length);binary=raw[28+length:28+length+blen]
    def accessor(ai):
        a=g['accessors'][ai];v=g['bufferViews'][a['bufferView']];dt={5126:'<f4',5125:'<u4',5123:'<u2',5122:'<i2',5121:'u1',5120:'i1'}[a['componentType']];n={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[a['type']];dtype=np.dtype(dt);stride=v.get('byteStride',n*dtype.itemsize);offset=v.get('byteOffset',0)+a.get('byteOffset',0)
        out=np.ndarray((a['count'],n),dtype=dtype,buffer=binary,offset=offset,strides=(stride,dtype.itemsize)).copy()
        if a.get('normalized'):out=out.astype(float)/np.iinfo(dtype).max
        return out.astype(float)
    parent={child:i for i,n in enumerate(g['nodes']) for child in n.get('children',[])};local={i:trs(n) for i,n in enumerate(g['nodes'])};original_world={}
    def tree_world(i,locals,cache):
        if i not in cache:cache[i]=(tree_world(parent[i],locals,cache) if i in parent else np.eye(4))@locals[i]
        return cache[i]
    for i in local:tree_world(i,local,original_world)
    pose=json.loads(Path(pose_path).read_text()) if pose_path else None
    outer=np.eye(4)
    if pose and 'jointLocals' in pose and not rest_control:
        for i,n in enumerate(g['nodes']):
            if n.get('name') in pose['jointLocals']:local[i]=np.array(pose['jointLocals'][n['name']]).reshape(4,4).T
        outer=np.array(pose['mmFromGLTF']).reshape(4,4).T
    elif pose and 'angles' in pose:
        source=json.loads(Path(source_path).read_text());bones=source['bones'];names=[b['name'] for b in bones];rest=np.array([b['matrix'] for b in bones]);inv=np.linalg.inv(rest);posed=[]
        for i,b in enumerate(bones):
            p=names.index(b['parent']) if b['parent'] else -1;relative=inv[p]@rest[i] if p>=0 else rest[i];basis=np.eye(4);basis[:3,:3]=euler_xyz([0,0,0] if rest_control else pose['angles'][b['name']]);posed.append((posed[p]@relative if p>=0 else relative)@basis)
        deform=np.array(posed)@inv;C=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1.]])
        wanted={}
        for i,node in enumerate(g['nodes']):
            if node.get('name') in names:wanted[i]=C@deform[names.index(node['name'])]@C.T@original_world[i]
        for i,mat in wanted.items():local[i]=np.linalg.inv(wanted.get(parent.get(i),original_world.get(parent.get(i),np.eye(4))))@mat
        q=np.array(pose['q']);globalmm=np.eye(4);globalmm[:3,:3]=euler_xyz(q[:3])@np.diag([-1,1,1])*q[6];globalmm[:3,3]=q[3:6];outer=globalmm@C.T
    elif not baked_mm:
        # Rest-only original hand convention; isotropic10mm/native unit and glTF Y-up→canonical.
        C=np.array([[1,0,0,0],[0,0,1,0],[0,-1,0,0],[0,0,0,1.]])
        outer=np.diag([-10.,10.,10.,1.])@C.T
    world={}
    for i in local:tree_world(i,local,world)
    meshes={}
    for ni,node in enumerate(g['nodes']):
        if 'mesh' not in node:continue
        for pi,prim in enumerate(g['meshes'][node['mesh']]['primitives']):
            if prim.get('mode',4)!=4:continue
            attrs=prim['attributes'];v=accessor(attrs['POSITION']);vh=np.column_stack((v,np.ones(len(v))));indices=accessor(prim['indices']).astype(int).reshape(-1,3) if 'indices'in prim else np.arange(len(v)).reshape(-1,3)
            if 'skin'in node:
                sk=g['skins'][node['skin']];ibm=accessor(sk['inverseBindMatrices']).reshape(-1,4,4).transpose(0,2,1);mats=np.array([world[j] for j in sk['joints']])@ibm;j=accessor(attrs['JOINTS_0']).astype(int);w=accessor(attrs['WEIGHTS_0']);blended=(mats[j]*w[:,:,None,None]).sum(1)
                if 'JOINTS_1'in attrs:
                    j1=accessor(attrs['JOINTS_1']).astype(int);w1=accessor(attrs['WEIGHTS_1']);blended+=(mats[j1]*w1[:,:,None,None]).sum(1)
                output=np.einsum('vij,vj->vi',blended,vh)@outer.T
                orientationDet=float(np.linalg.det(outer[:3,:3]))*float(np.median(np.linalg.det(blended[:,:3,:3])))
                normalLinear=np.einsum('ij,vjk->vik',outer[:3,:3],blended[:,:3,:3])
            else:
                output=vh@world[ni].T@outer.T
                orientationDet=float(np.linalg.det((outer@world[ni])[:3,:3]))
                normalLinear=np.tile((outer@world[ni])[:3,:3],(len(v),1,1))
            normalWorld=None
            if 'NORMAL' in attrs:
                normalWorld=np.einsum('vji,vj->vi',np.linalg.inv(normalLinear),accessor(attrs['NORMAL']))
                normalWorld/=np.maximum(np.linalg.norm(normalWorld,axis=1)[:,None],1e-20)
            # Canonical rest-position IDs weld glTF UV seams, but never merge separately posed fingers.
            _,canonical=np.unique(np.round(v,7),axis=0,return_inverse=True)
            if orientationDet<0:indices=indices[:,[0,2,1]]
            name=node.get('name',f'mesh-{ni}')+(f'-{pi}'if pi else'')
            meshes[name]={'positions':output[:,:3],'triangles':indices,'canonicalIds':canonical,'rest':v,'authoredNormalsWorld':normalWorld,'orientationDeterminantSign':-1 if orientationDet<0 else 1,'boneNames':[g['nodes'][jj]['name'] for jj in g['skins'][node['skin']]['joints']] if 'skin'in node else [],'jointIndices':j if 'skin'in node else None,'jointWeights':w if 'skin'in node else None,'hasSkin':'skin'in node,'jointInfluences':int((accessor(attrs['WEIGHTS_0'])>1e-8).sum(1).max()) if 'WEIGHTS_0'in attrs else 0}
    return meshes,{'glbSHA256':hashlib.sha256(raw).hexdigest(),'glb':str(glb),'pose':str(pose_path)if pose_path else None,'restControl':rest_control,'bakedMm':baked_mm,'poseData':pose}
