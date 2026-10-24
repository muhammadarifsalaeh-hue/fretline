"""Scratch consistent audit source: original GLB's actual normalized four skin weights.
No geometry or app change. UV-seam duplicates checked for identical skin weights.
"""
import os
from pathlib import Path
P=Path(os.environ.get('FRETLINE_STAGE3_DIR', '/tmp/fretline-stage3-assets'))
exec((P/'prove-runtime-transfer.py').read_text().split('reports=[]')[0])
import copy
compatible=copy.deepcopy(src);checks=[]
for node in [n for n in g['nodes'] if 'mesh' in n]:
 prim=g['meshes'][node['mesh']]['primitives'][0];att=prim['attributes'];v=access(att['POSITION']);j=access(att['JOINTS_0']).astype(int);w=access(att['WEIGHTS_0']);native=next(m for m in compatible['meshes'] if m['name']==node['name']);nv=np.array([v['co'] for v in native['verts']]);nvh=np.column_stack((nv,np.ones(len(nv))));dist,mapping=cKDTree((nvh@C.T)[:,:3]).query(v);gw=np.zeros((len(v),len(names)))
 for col in range(4):
  for row in range(len(v)):gw[row,names.index(g['nodes'][skin['joints'][j[row,col]]]['name'])]+=w[row,col]
 seamdiff=0;missing=0
 for ni,vertex in enumerate(native['verts']):
  match=np.flatnonzero(mapping==ni)
  if len(match)==0:missing+=1;continue
  seamdiff=max(seamdiff,float(np.abs(gw[match]-gw[match[0]]).max()));vertex['weights']=gw[match[0]].tolist()
 checks.append({'mesh':node['name'],'uvDuplicateWeightMaxDifference':seamdiff,'missingNativeVertices':missing})
compatible['auditOnlyNote']='Scratch weight-equivalent native representation of original exported GLB. Geometry unchanged. Native source has up to6 influences; original GLB normalized top4. Use for actualruntimecollision audit only; this is not a new model export.'
(P/'fk-source-gltf-compatible.json').write_text(json.dumps(compatible))
print(json.dumps(checks,indent=2))
# Verify mathematical transfer against exact GLB-compatible weights, retaining original comparison separately.
script=(P/'prove-runtime-transfer.py').read_text().replace("src=json.loads((P/'fk-source.json').read_text())","src=json.loads((P/'fk-source-gltf-compatible.json').read_text())").replace("'runtime-transfer-audit.json'","'runtime-transfer-gltf-compatible-audit.json'")
exec(compile(script,'gltf-compatible-runtime-proof','exec'))
