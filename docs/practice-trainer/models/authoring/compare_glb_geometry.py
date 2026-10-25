"""Verify a material-only revision preserves every geometry and skinning byte.

Usage: python compare_glb_geometry.py BEFORE.glb AFTER.glb [REPORT.json] [--hand-only]
"""
import hashlib,json,struct,sys
from pathlib import Path

def read(path):
    raw=path.read_bytes();offset=12;document=None;binary=None
    while offset<len(raw):
        size,kind=struct.unpack_from('<II',raw,offset)
        chunk=raw[offset+8:offset+8+size];offset+=8+size
        if kind==0x4E4F534A:document=json.loads(chunk)
        elif kind==0x004E4942:binary=chunk
    return raw,document,binary

def accessor(document,binary,index):
    item=document['accessors'][index];view=document['bufferViews'][item['bufferView']]
    components={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4,'MAT4':16}[item['type']]
    width=components*{5120:1,5121:1,5122:2,5123:2,5125:4,5126:4}[item['componentType']]
    start=view.get('byteOffset',0)+item.get('byteOffset',0);stride=view.get('byteStride',width)
    return b''.join(binary[start+i*stride:start+i*stride+width] for i in range(item['count']))

hand_only='--hand-only' in sys.argv;args=[a for a in sys.argv[1:] if a!='--hand-only']
before=Path(args[0]);after=Path(args[1]);raw1,g1,b1=read(before);raw2,g2,b2=read(after)
def bone_nodes(document):
    joints={j for skin in document['skins'] for j in skin['joints']}
    return {document['nodes'][j]['name']:document['nodes'][j] for j in joints}
report={'scope':'hand and complete rig' if hand_only else 'all meshes and complete rig','beforeSha256':hashlib.sha256(raw1).hexdigest(),'afterSha256':hashlib.sha256(raw2).hexdigest(),'nodesIdentical':g1['nodes']==g2['nodes'],'boneNodesIdentical':bone_nodes(g1)==bone_nodes(g2),'skinDefinitionsIdentical':g1['skins']==g2['skins'],'meshes':[]}
assert (report['boneNodesIdentical'] if hand_only else report['nodesIdentical']) and report['skinDefinitionsIdentical']
for old,new in zip(g1['meshes'],g2['meshes']):
    assert old['name']==new['name'] and len(old['primitives'])==len(new['primitives'])
    if hand_only and 'Hand' not in old['name']:continue
    entry={'name':old['name'],'allAttributeBytesIdentical':True,'allIndexBytesIdentical':True}
    for primitive1,primitive2 in zip(old['primitives'],new['primitives']):
        assert primitive1['attributes'].keys()==primitive2['attributes'].keys()
        for name,index1 in primitive1['attributes'].items():
            assert accessor(g1,b1,index1)==accessor(g2,b2,primitive2['attributes'][name]),name
        assert accessor(g1,b1,primitive1['indices'])==accessor(g2,b2,primitive2['indices'])
    report['meshes'].append(entry)
for skin1,skin2 in zip(g1['skins'],g2['skins']):
    assert accessor(g1,b1,skin1['inverseBindMatrices'])==accessor(g2,b2,skin2['inverseBindMatrices'])
report['inverseBindBytesIdentical']=True
if len(args)>2:Path(args[2]).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
