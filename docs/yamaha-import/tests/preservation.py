"""Bind this import to the old project and stable records, never a count-only check."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3]
BASE='decd5544ade430530ac7c1e37ae463f251c90d50'
IDS=['yamaha-fsx830c','yamaha-fsx800c','yamaha-fs800','yamaha-fgx820c','yamaha-fg800m','yamaha-fg820l','yamaha-fs830','yamaha-fg820','yamaha-fgx800c','yamaha-fg840','yamaha-fg850','yamaha-fg800j','yamaha-fg820-12','yamaha-fs850','yamaha-fg830','yamaha-fsx820c','yamaha-fs820','yamaha-fg800']
def old(path):return subprocess.check_output(['git','show',BASE+':'+path],cwd=ROOT)
def sha(b):return hashlib.sha256(b).hexdigest()
checks=[]
def check(name,value,**evidence):
 checks.append({'name':name,'passed':bool(value),**evidence})
 print(('PASS ' if value else 'FAIL ')+name,flush=True)
old_records=json.loads(old('src/data/catalog/reviewedGuitars.json'));records=json.loads((ROOT/'src/data/catalog/reviewedGuitars.json').read_bytes())
check('Reviewed record ID set unchanged',set(old_records)==set(records),count=len(records))
check('All18 supplied models map to pre-existing IDs',len(IDS)==18 and len(set(IDS))==18 and all(k in old_records for k in IDS))
check('No model brand/name/identity changed',all(all(records[k].get(f)==v.get(f) for f in ['id','brand','name','category']) for k,v in old_records.items()))
check('Every other reviewed record unchanged',all(records[k]==v for k,v in old_records.items() if k not in IDS))
files=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src/features/practice'],cwd=ROOT,text=True).splitlines()
changed=[p for p in files if not (ROOT/p).is_file() or (ROOT/p).read_bytes()!=old(p)]
check('All original Practice files byte-identical',len(files)>0 and not changed,count=len(files),changed=changed)
protected=['src/data/catalog/projectArtwork.json','src/data/catalog/imageRights.json','src/data/catalog/catalogPolicy.json','src/data/guitars.js','src/data/quiz.js','src/utils/quizScoring.js','src/context/ShopContext.jsx']
changed=[p for p in protected if (ROOT/p).read_bytes()!=old(p)]
check('Original musical/product IDs, image rights, shop and quiz preserved',not changed,files=protected,changed=changed)
pagefiles=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src/pages','src/components'],cwd=ROOT,text=True).splitlines()
# The only allowed product-UI extensions are tracked explicitly, never broad directory exemptions.
allowed={'src/components/detail/SpecTable.jsx','src/components/detail/DataStatusNote.jsx','src/components/guitar/PriceSourceNote.jsx','src/pages/GuitarDetailPage.jsx','src/components/compare/CompareVerdicts.jsx'}
changed=[p for p in pagefiles if p not in allowed and (not (ROOT/p).is_file() or (ROOT/p).read_bytes()!=old(p))]
check('Unrelated pages and components byte-identical',not changed,count=len(pagefiles)-len(allowed),changed=changed)
sourcefiles=subprocess.check_output(['git','ls-tree','-r','--name-only',BASE,'src'],cwd=ROOT,text=True).splitlines()
source_allowed=allowed|{'src/data/catalog/reviewedGuitars.json','src/data/additionalSpecifications.js','src/data/guitarImages.js','src/i18n/th.js','src/i18n/en.js','src/utils/dataTrust.js'}
changed=[p for p in sourcefiles if p not in source_allowed and (not (ROOT/p).is_file() or (ROOT/p).read_bytes()!=old(p))]
check('Every other original source/data/asset is byte-identical',not changed,count=len(sourcefiles)-len(source_allowed),changed=changed,allowedChanges=sorted(source_allowed))
report={'baselineCommit':BASE,'importedIds':IDS,'checks':checks,'passed':all(c['passed'] for c in checks)}
(ROOT/'docs/yamaha-import/tests/preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(not report['passed'])
