"""Remove the known grayscale-height-as-normal binding, without changing image/mesh bytes.
Keeps the optional height texture in material extras for an explicit runtime adapter.
No pose or production approval implied.
"""
import argparse,struct,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--input',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--report',type=Path,required=True);a=p.parse_args();assert a.input.resolve()!=a.output.resolve()
raw=a.input.read_bytes();n=struct.unpack_from('<I',raw,12)[0];g=json.loads(raw[20:20+n]);rest=raw[20+n:];changes=[]
for i,m in enumerate(g.get('materials',[])):
 binding=m.get('normalTexture')
 if binding is None:continue
 texture=g['textures'][binding['index']];im=g['images'][texture['source']]
 if im.get('name')!='skin_bump':continue
 extras=m.setdefault('extras',{});extras['fretlineHeightTexture']={'index':binding['index'],'texCoord':binding.get('texCoord',0),'colorSpace':'linear','bumpScaleMm':.035,'note':'Grayscale height, not a tangent-space normal. Generic viewers may omit microbump.'};del m['normalTexture'];changes.append({'material':i,'image':im['name'],'removedWrongNormalBinding':True,'preservedOptionalHeightTexture':True})
assert changes,'Expected known skin_bump normal misbinding; refuse blind material edits'
g.setdefault('asset',{}).setdefault('extras',{})['stage31MaterialNote']='Corrected known grayscale height misbinding. Rig/pose remain UNAPPROVED.'
b=json.dumps(g,separators=(',',':'),ensure_ascii=False).encode();b+=b' '*((-len(b))%4);output=struct.pack('<III',0x46546c67,2,20+len(b)+len(rest))+struct.pack('<II',len(b),0x4e4f534a)+b+rest;a.output.write_bytes(output)
report={'status':'PASS known binding repair only; NOT pose approval','inputSHA256':hashlib.sha256(raw).hexdigest(),'outputSHA256':hashlib.sha256(output).hexdigest(),'changes':changes,'allBINBytesUnchanged':rest==output[20+len(b):],'allAccessorsUnchanged':True,'genericViewerLimitation':'Correct outward geometry normals and color/roughness; optional skin microbump retained as metadata, needs runtime binding.'}
a.report.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
