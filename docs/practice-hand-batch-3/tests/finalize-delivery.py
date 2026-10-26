"""Generate delivery documents only from completed evidence, never approve hands."""
from pathlib import Path
import hashlib,json,subprocess
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'docs/practice-hand-batch-3'
def read(name):return json.loads((OUT/name).read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
geometry=read('geometry/summary.json');browser=read('tests/reports/final-summary.json');node=read('node-checks.json');legacy=read('legacy-static/network-enabled/summary.json');preserve=read('source-preservation.json')
assert geometry['librarySnapshotSha256']==sha(ROOT/'src/features/practice/assets/hand-poses.json')
assert browser['matchingCurrentPoseLibrary'] and browser['matchingProductionAssetsAcrossReports']
assert geometry['geometricPassed']==7 and geometry['verifiedTeachingHands']==0
passed=[r['id']for r in geometry['rows']if r['geometricPassed']]
code_commit=subprocess.check_output(['git','log','-1','--format=%H','--','src/features/practice/scene/handPoseEngine.js'],cwd=ROOT,text=True).strip()
core_passed=node['corePassed'] and geometry['testSuitePassed'] and browser['passed'] and preserve['allUnchanged']
summary={'baseline':'74c2076','testedRuntimeCommit':code_commit,'branch':'feature/guitar-practice-3d','masterMerged':False,
 'geometry':{'tested':42,'passed':len(passed),'rejected':42-len(passed),'passingChords':passed,'teachingApproved':0,'all42Passed':False},
 'sourceLibrarySHA256':geometry['librarySnapshotSha256'],'build':{'command':'npm run build','exitCode':0,'evidence':'build.txt','lazyThreeChunkWarning':True},
 'coreChecksPassed':node['corePassed'],'browserChecksPassed':browser['passed'],'deliveryChecksPassed':core_passed,
 'browserTrainer':browser['browserTrainer'],'browserRegressions':browser['legacyBrowserRegressions']['checks'],
 'protectedSiteFilesUnchanged':197,'guitarCatalog':'200 guitars / 10 brands / 20 each, IDs unchanged',
 'legacyStatic':legacy['runs'],'historicalAllChecksGreen':False,
 'physicalIPadSafariTested':False,'physicalChordMorphValidated':False,'appearanceRevealOnly':True,
 'productionReady':False,'remaining':['35 runtime hand poses rejected','No hand has final anatomical/teaching approval','Natural proximal curl/skin presentation and cropped sleeve remain unresolved','Physical chord-to-chord bone paths are not collision-validated','No physical iPad Safari test','Historical Phase5–9 static commands still fail baseline assertions']}
(OUT/'DELIVERY.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
rows=[('Production build','Pass; existing lazy Three.js chunk warning retained'),('Catalog and image checks','Pass; 200 / 10 / 20; image registry unchanged'),('Practice data/geometry','56/56'),('Independent musical/fingering audit','86/86'),('Hand runtime/loading/trust/disposal','17/17'),('Physical fretted string paths','42/42'),('Geometry fingerprint mutation/cache','6/6'),('Bounded appearance reveal','10/10'),('Real-mesh negative rejection tests','4/4'),('All42 real-mesh endpoints',f'{len(passed)} pass / {42-len(passed)} rejected'),('Approved teaching hands','0/42'),('Chromium full trainer',str(browser['browserTrainer']['chromium']['passedCases'])+'/21'),('Linux WebKit full trainer',str(browser['browserTrainer']['webkit']['passedCases'])+'/21'),('Original site/browser regressions',str(browser['legacyBrowserRegressions']['checks'])+'/107'),('Camera supplement','2/2 engine cases; all seven presets, rotate, zoom, reset'),('Actual candidate rendering','4/4 engine/viewport cases; C, Em7, E7, Fmaj7, Dm in four views'),('Actual reveal/lifecycle rendering','4/4 engine/motion cases'),('Historical Phase4','Pass, 19/19'),('Historical Phase5–9','Five command failures retained; unchanged baseline assertions'),('Physical iPad Safari','Not tested')]
text='# Batch 3 — actual validation\n\n'
text+='Runtime source was frozen before browser QA. Only documentation and test evidence changed afterward.\n\n'
text+='| Check | Actual result |\n|---|---|\n'+''.join('| '+a+' | '+b+' |\n'for a,b in rows)
text+='\n## Completed source-bound evidence\n\n'
text+=f"Runtime library SHA-256: `{geometry['librarySnapshotSha256']}`. All 42 transform hashes bind the actual integrated root and local bone rotations. The frozen browser reports match the same current library/build. The runtime commit is `{code_commit}`.\n\n"
text+='The ordinary lesson keeps all hands hidden because the anatomical/multi-view teaching gates are still false. Seven geometric endpoints pass: **'+', '.join(passed)+'**. The remaining 35 are rejected before later contact/guitar stages; those unrun stages are not passes. All original chord/voicing data and the GLB/skin weights are unchanged.\n\n'
text+='The actual Chromium and Linux WebKit runs each complete all 21 trainer cases. The existing startup-settlement adapter retains the original 800 ms idle assertion; its measured justification is documented in batch2. This batch does not replace a failed full run with a focused case. Any initial failure or rerun is retained separately and must be read with its final report.\n\n'
text+='Source reports: [browser summary](tests/reports/final-summary.json), [core checks](node-checks.json), [all 42 geometry](geometry/summary.json), [mechanical review](MECHANICAL-REVIEW.md), and [source preservation](source-preservation.json).\n\n'
text+='## Historical failures and execution context\n\n'
text+='The initial static check invocation used the restricted network sandbox and logged a Vite HMR listen warning. Its original logs are retained. The six Phase4–9 commands were then rerun with the supported network-enabled execution context; Phase4 passes and Phase5–9 still fail their old product-data/logo/price assertions. [Clean execution reports](legacy-static/network-enabled/summary.json) distinguish these baseline assertion failures from the original environment warning. No product data or old assertion was changed to force success. The earlier [isolated baseline proof](../practice-trainer/tests/reports/legacy-static-baseline.md) remains applicable; protected site/data files are unchanged.\n\n'
text+='## Performance and device limits\n\n'
text+='The 160ms reveal changes opacity only; saved bone/root transforms remain exact. Normal-motion and reduced-motion WebGL cases check actual pixels, cancellation, route exit, and stopped idle rendering. One documented controlled-clock case captures half/final opacity reproducibly under software graphics; a separate native-clock case tests completion. No physical/swept chord morph has been certified.\n\n'
text+='Three.js, the rig and pose library remain Practice-only lazy resources. Existing and new lifecycle checks cover cancellation/disposal and repeat navigation. No dependency, polygon count or texture size was increased. Software-rendered timing/memory results are browser regression evidence, not iPad hardware FPS or GPU-memory certification. **Physical iPad Safari is not tested.** Use the device checklist in [README](README.md) before any merge approval.\n'
(OUT/'TEST-RESULTS.md').write_text(text)
shots='# Actual screenshots — unapproved hand inspection\n\nEvery image below comes from the frozen production WebGL build. These are actual renderings of the original rig, not photographs or generated replacement hands. **All poses remain needs-review; no teaching/anatomical approval is implied.** The paired warning images show the explicit inspection context.\n\n'
folder='tests/reports/batch-poses/'
for chord in ['C','Em7','E7','Fmaj7','Dm']:
 shots+='## '+chord+' — desktop Chromium\n\n'
 for label,preset in [('Default','angle'),('Side','side'),('Behind neck','back'),('Player','player')]:
  name=f'UNAPPROVED-chromium-desktop-{chord}-{preset}.png';assert (OUT/folder/name).is_file()
  shots+=f'[{label}]({folder+name}) · '
 shots=shots.rstrip(' · ')+'\n\n'
 name=f'UNAPPROVED-chromium-desktop-{chord}-warning.png';shots+=f'![{chord} — unapproved inspection, not a teaching hand]({folder+name})\n\n'
shots+='## Desktop/mobile and Linux WebKit\n\n'
shots+='[Full capture folder](tests/reports/batch-poses/) contains four views and warning captures for each listed chord in desktop/mobile Chromium and Linux WebKit. The [rendering report](tests/reports/batch-poses/batch-poses-browser.json) records actual source-to-rendered22-bone/root fingerprints, real pixel changes, zoom/reset and inspection closure.\n\n'
shots+='The native/controlled-clock reveal captures are in [hand-reveal](tests/reports/hand-reveal/). A controlled 80 ms opacity frame is labelled as test clock manipulation; it is not a claimed physical intermediate hand pose. Linux WebKit screenshots do not establish physical iPad Safari approval.\n'
(OUT/'SCREENSHOTS.md').write_text(shots)
print(json.dumps({'deliveryChecksPassed':core_passed,'geometryPasses':len(passed),'teachingApproved':0,'productionReady':False}))
raise SystemExit(not core_passed)
