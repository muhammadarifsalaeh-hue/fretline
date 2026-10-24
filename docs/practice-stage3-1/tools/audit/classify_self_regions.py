import sys,json,numpy as np,collections
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent));from skin_from_glb import evaluate
meshmeta,_=evaluate(sys.argv[1],sys.argv[2],sys.argv[3]);report=json.load(open(sys.argv[4]));out={}
for name,selfdata in report['selfIntersections'].items():
 m=meshmeta[name];labels=[];examples={}
 for evidence in selfdata['confirmedEvidence']:
  row=[]
  for ti in evidence['pair']:
   inds=m['triangles'][ti];j=m['jointIndices'][inds];w=m['jointWeights'][inds];tot=np.zeros(len(m['boneNames']));np.add.at(tot,j.ravel(),w.ravel());row.append(m['boneNames'][np.argmax(tot)])
  key=tuple(sorted(row));labels.append(key);examples.setdefault(key,evidence)
 out[name]=[{'bones':list(pair),'trianglePairCount':count,'example':examples[pair]}for pair,count in collections.Counter(labels).most_common()]
print(json.dumps(out,indent=2));Path(sys.argv[5]).write_text(json.dumps(out,indent=2))
