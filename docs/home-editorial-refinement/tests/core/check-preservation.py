"""Verify protected Fretline source/assets against the exact prior delivery.

This check deliberately excludes authorized Home presentation changes. It never
marks an unverified 3D hand as correct; it checks existing Practice inputs did not
change during this Home refinement.
"""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
BASELINE='0f994b4990211acc9151293c9f17a3aa65a156ef'
tracked=subprocess.check_output(['git','ls-tree','-r','--name-only',BASELINE],cwd=ROOT,text=True).splitlines()
prefixes=(
 'src/data/catalog/','src/assets/guitars/','src/features/practice/',
 'src/components/quiz/','src/components/catalog/','src/components/detail/',
 'src/components/guitar/','src/utils/','src/context/',
)
exact={
 'src/data/guitars.js','src/data/guitarImages.js','src/data/quiz.js',
 'src/data/brands.js','src/data/categories.js','src/data/additionalSpecifications.js',
 'src/data/navigation.js','src/pages/FindMyGuitarPage.jsx','src/styles/premium-quiz.css',
 'src/pages/CatalogPage.jsx','src/pages/GuitarDetailPage.jsx','src/pages/WishlistPage.jsx',
 'src/pages/PracticePage.jsx','src/styles/practice.css','src/styles/premium-compare.css',
 'src/pages/ComparePage.jsx','src/components/layout/Footer.jsx','src/components/layout/MobileMenu.jsx','src/i18n/th.js','src/i18n/en.js',
 'src/components/layout/CompareBar.jsx',
 'src/hooks/useBrandMarquee.js','src/styles/home-brands.css','package.json','package-lock.json',
}
# This credit component gains licensed category images; no product behavior.
authorized={'src/components/detail/HomePhotographyCredits.jsx'}
selected=[p for p in tracked if (p.startswith(prefixes) or p in exact or p.startswith('src/components/compare/')) and p not in authorized and p!='src/components/compare/CompareSection.jsx']
sha=lambda b:hashlib.sha256(b).hexdigest()
rows=[]
for name in selected:
 before=subprocess.check_output(['git','show',f'{BASELINE}:{name}'],cwd=ROOT)
 actual=(ROOT/name).read_bytes() if (ROOT/name).exists() else b''
 rows.append({'path':name,'baselineSHA256':sha(before),'actualSHA256':sha(actual),'unchanged':actual==before})
old_compare=subprocess.check_output(['git','show',f'{BASELINE}:src/pages/ComparePage.jsx'],cwd=ROOT,text=True)
compare_unchanged=(ROOT/'src/pages/ComparePage.jsx').read_text()==old_compare
facts_js="""
import {readCatalog} from './scripts/lib/catalog.mjs';
import {PRACTICE_CHORDS} from './src/features/practice/data/chords.js';
const all=readCatalog(), brands={}, categories={};
for(const g of all){brands[g.brand]=(brands[g.brand]??0)+1;categories[g.category]=(categories[g.category]??0)+1;}
console.log(JSON.stringify({models:all.length,uniqueIds:new Set(all.map(g=>g.id)).size,brands,categories,chords:PRACTICE_CHORDS.length,chordIds:PRACTICE_CHORDS.map(g=>g.id),orderedGuitarIds:all.map(g=>g.id)}));
"""
facts=json.loads(subprocess.check_output(['node','--input-type=module','-e',facts_js],cwd=ROOT,text=True))
passed=all(row['unchanged'] for row in rows) and compare_unchanged and facts['models']==200 and facts['uniqueIds']==200 and len(facts['brands'])==10 and all(n==20 for n in facts['brands'].values()) and facts['chords']==42
report={'baselineCommit':BASELINE,'protectedFiles':len(rows),'changedProtectedFiles':[r['path'] for r in rows if not r['unchanged']],'comparePageByteIdentical':compare_unchanged,'facts':facts,'files':rows,'passed':passed,'physicalIPadSafariTested':False,'note':'Byte preservation and chord-data checks do not certify anatomical hand-pose accuracy. Dedicated Quiz and Compare pages, components, styles, question data, scoring and saved selections are byte-identical.'}
(OUT/'preservation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('facts','files')},ensure_ascii=False))
print('Catalog:',facts['models'],'models /',len(facts['brands']),'brands /20 each;',facts['chords'],'original chords')
assert passed,report['changedProtectedFiles']
