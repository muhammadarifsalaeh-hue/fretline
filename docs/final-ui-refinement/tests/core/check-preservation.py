"""Protect original product/chord/solver/scoring bytes during scoped UI refinement.

The explicitly requested presentation files are excluded from byte equality, but
Practice's pre-render selection, camera, scene lifecycle and review gates are
also compared after removing only retired display-label computations.
"""
from pathlib import Path
import hashlib, json, re, subprocess

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parent
BASELINE = '985d0c4898bb02961d25752d8ad0d2dc2ccd1588'
AUTHORIZED_PRESENTATION = {
    'src/pages/HomePage.jsx', 'src/pages/CatalogPage.jsx', 'src/pages/ComparePage.jsx',
    'src/pages/PracticePage.jsx', 'src/components/quiz/QuizFlow.jsx',
    'src/components/quiz/QuizHero.jsx', 'src/components/quiz/QuizIntro.jsx',
    'src/styles/premium-quiz.css', 'src/styles/premium-compare.css',
    'src/features/practice/components/GuitarNeckViewer.jsx',
}
AUTHORIZED_NEW_PRESENTATION = {
    'src/components/home/GuitarPracticeCard.jsx',
    'src/styles/home-feature-restoration.css',
    'src/styles/catalog-refinement.css', 'src/styles/practice-refinement.css',
}
EXACT = {'package.json', 'package-lock.json', 'vite.config.js', 'jsconfig.json',
         'tailwind.config.js', 'postcss.config.js', 'index.html'}
tracked = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', BASELINE], cwd=ROOT, text=True).splitlines()
selected = [name for name in tracked if (name.startswith(('src/', 'scripts/', 'public/')) or name in EXACT)
            and name not in AUTHORIZED_PRESENTATION]
current = set(subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '--', 'src', 'scripts', 'public'], cwd=ROOT, text=True).splitlines())
new_files = sorted(current - set(tracked))
unexpected_new_files = sorted(set(new_files) - AUTHORIZED_NEW_PRESENTATION)
sha = lambda data: hashlib.sha256(data).hexdigest()
old = lambda name: subprocess.check_output(['git', 'show', f'{BASELINE}:{name}'], cwd=ROOT)
rows = []
for name in selected:
    before = old(name)
    actual = (ROOT / name).read_bytes() if (ROOT / name).exists() else b''
    rows.append({'path': name, 'baselineSHA256': sha(before), 'actualSHA256': sha(actual), 'unchanged': actual == before})

# Rendering is authorized to change; these comparisons protect existing behavior.
def before_render(source):
    return source[source.index('export default function '):source.index('\n  return (')]

def normalized_viewer(source):
    block = before_render(source)
    block = re.sub(r'  const handMessage = .*?;\n', '', block, flags=re.S)
    block = re.sub(r'  const handReason = [^\n]*;\n', '', block)
    return block

def normalized_practice(source):
    return re.sub(r'  const statusLabel = [^\n]*;\n', '', before_render(source))

viewer = 'src/features/practice/components/GuitarNeckViewer.jsx'
practice = 'src/pages/PracticePage.jsx'
behavior = {
    'viewerSceneLifecycleCameraActionsAndReviewGatesUnchanged': normalized_viewer(old(viewer).decode()) == normalized_viewer((ROOT / viewer).read_text()),
    'practiceChordSelectionFilteringNavigationAndFingerCoordinatesUnchanged': normalized_practice(old(practice).decode()) == normalized_practice((ROOT / practice).read_text()),
}
home = (ROOT / 'src/pages/HomePage.jsx').read_text()
home_sequence = re.findall(r'<(Hero|Brands|Categories|GuitarPracticeCard|FindMyGuitar|CompareSection|FeaturedGuitars)\s*/>', home)
home_restoration = {
    'onePracticeCardBeforeExactOriginalFindAndCompare': home_sequence == [
        'Hero', 'Brands', 'Categories', 'GuitarPracticeCard', 'FindMyGuitar', 'CompareSection', 'FeaturedGuitars'],
    'retiredGuitarModesComponentAbsent': 'GuitarModes' not in home and not (ROOT / 'src/components/home/GuitarModes.jsx').exists(),
    'retiredGuitarModesStylesAbsent': not (ROOT / 'src/styles/home-guitar-modes.css').exists(),
    'onlyAuthorizedNewPresentationFiles': not unexpected_new_files,
}
facts_js = """
import { readCatalog } from './scripts/lib/catalog.mjs';
import { PRACTICE_CHORDS, BY_ID } from './src/features/practice/data/chords.js';
const catalog=readCatalog(),brands={},categories={};
for(const g of catalog){brands[g.brand]=(brands[g.brand]??0)+1;categories[g.category]=(categories[g.category]??0)+1;}
console.log(JSON.stringify({models:catalog.length,uniqueIds:new Set(catalog.map(g=>g.id)).size,brands,categories,
  orderedGuitarIds:catalog.map(g=>g.id),chords:PRACTICE_CHORDS.length,chordIds:PRACTICE_CHORDS.map(g=>g.id),
  cMajor:{voicing:BY_ID.C.voicing,frets:BY_ID.C.frets,fingers:BY_ID.C.fingers,notes:BY_ID.C.notes,barres:BY_ID.C.barres,openStrings:BY_ID.C.openStrings,mutedStrings:BY_ID.C.mutedStrings},
  handPoseStatuses:PRACTICE_CHORDS.reduce((out,c)=>(out[c.handPose.status]=(out[c.handPose.status]??0)+1,out),{})}));
"""
facts = json.loads(subprocess.check_output(['node', '--input-type=module', '-e', facts_js], cwd=ROOT, text=True))
assert facts['cMajor']['voicing'] == 'x32010'
assert facts['cMajor']['frets'] == [None, 3, 2, 0, 1, 0]
assert facts['cMajor']['fingers'] == [None, 3, 2, None, 1, None]
assert facts['cMajor']['openStrings'] == [3, 1]
assert facts['cMajor']['mutedStrings'] == [6]
passed = (all(row['unchanged'] for row in rows) and all(behavior.values()) and all(home_restoration.values())
          and facts['models'] == facts['uniqueIds'] == 200 and len(facts['brands']) == 10
          and all(count == 20 for count in facts['brands'].values()) and facts['chords'] == 42)
report = {
    'baselineCommit': BASELINE, 'protectedFiles': len(rows),
    'changedProtectedFiles': [row['path'] for row in rows if not row['unchanged']],
    'authorizedPresentationFiles': sorted(AUTHORIZED_PRESENTATION),
    'authorizedNewPresentationFiles': sorted(AUTHORIZED_NEW_PRESENTATION),
    'actualNewPresentationFiles': new_files, 'unexpectedNewSourceFiles': unexpected_new_files,
    'homeRestoration': home_restoration,
    'originalPracticeBehavior': behavior, 'facts': facts, 'files': rows, 'passed': passed,
    'physicalIPadSafariTested': False,
    'note': 'Preserves source data, accuracy criteria and solver/geometry; it does not certify anatomical hand poses. All original scripts/tests remain byte-identical. No hand pose is promoted to verified.',
}
(OUT / 'preservation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('facts', 'files', 'authorizedPresentationFiles', 'authorizedNewPresentationFiles')}, ensure_ascii=False))
print('Catalog:', facts['models'], 'models /', len(facts['brands']), 'brands /20 each;', facts['chords'], 'original chords; C Major x32010')
assert passed, {'changed': report['changedProtectedFiles'], 'behavior': behavior, 'home': home_restoration}
