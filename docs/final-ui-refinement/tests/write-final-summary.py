"""Consolidate final evidence, preserving initial harness diagnostics and retests."""
from pathlib import Path
import hashlib,json
from urllib.request import urlopen
ROOT=Path(__file__).resolve().parents[3]
DIR=Path(__file__).resolve().parent
paths=['final-ui/chromium-browser-results.json','final-ui-webkit/browser-results.json','final-home/browser-results.json','final-quiz-compare-chromium/browser-results.json','final-quiz-compare-landscape-retest/browser-results.json','final-quiz-compare-webkit/browser-results.json']
reports=[(name,json.loads((DIR/name).read_text())) for name in paths]
checks={};attempts=[];versions={};all_hashes={};conflicts=[]
for name,report in reports:
 versions.update(report.get('browserVersions',{}))
 for case in report['checks']:
  if case['case'] in checks:attempts.append({'case':case['case'],'supersededReport':checks[case['case']]['report'],'finalReport':name,'priorPassed':checks[case['case']]['passed'],'finalPassed':case['passed']})
  checks[case['case']]={**case,'report':name}
 for name2,digest in report['sourceAndBuildSHA256'].items():
  if name2 in all_hashes and all_hashes[name2]!=digest:conflicts.append(name2)
  all_hashes[name2]=digest
current_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in all_hashes}
provenance=json.loads((DIR/'qa-provenance.json').read_text())
before_stable=all(hashlib.sha256((DIR/name).read_bytes()).hexdigest()==digest for name,digest in provenance['beforeCaptureSHA256'].items())
nav=[];errors={key:[] for key in ['consoleErrors','runtimeErrors','networkErrors','failedRequests','harnessFailures']}
for name,report in reports:
 for key in errors:
  for error in report.get(key,[]):
   final=checks.get(error.get('case',''),{})
   resolved=key=='failedRequests' and name=='final-ui-webkit/browser-results.json' and error.get('case') in ['webkit-desktop-home-restored-three-card-group','webkit-landscape-home-restored-three-card-group'] and error.get('failure')=='Load request cancelled' and error.get('url','').endswith('/assets/practice-three-CP7LDGza.js') and final.get('report')=='final-home/browser-results.json' and final.get('passed') is True
   if resolved:nav.append({**error,'initialReport':name,'resolvedBy':final['report'],'cause':'Test intentionally left Practice before its lazy scene initialized; retest waits for completed scene and has zero failed requests.'})
   else:errors[key].append({'report':name,**error})
initial_failures=[{'report':name,**case} for name,r in reports for case in r['checks'] if case['passed'] is False]
current_stable=not conflicts and all_hashes==current_hashes and all(r.get('sourceAndBuildUnchangedDuringRun') for name,r in reports)
final_checks=list(checks.values());ui=[c for c in final_checks if not any(x in c['case'] for x in ['quiz-options','quiz-flow','six-result-fixtures','compare-interactions','responsive-320','untouched-page','actual-clipboard'])]
threeD={engine:{'all42':next(c['evidence'] for c in final_checks if c['case']==engine+'-practice-all42-accuracy'),'camera':next(c['evidence'] for c in final_checks if c['case']==engine+'-practice-camera-controls'),'fallback':next(c['evidence'] for c in final_checks if c['case']==engine+'-practice-injected-webgl-fallback')} for engine in ['chromium','webkit']}
summary={'baseURL':'http://127.0.0.1:5451','browserVersions':versions,'physicalIPadSafariTested':False,'finalDistinctChecks':len(final_checks),'passedChecks':sum(c['passed'] is True for c in final_checks),'unavailableChecks':[c['case'] for c in final_checks if c['passed'] is None],'uiPracticeHomeChecks':len(ui),'quizCompareChecks':len(final_checks)-len(ui),'unexpectedErrors':errors,'initialNavigationCancellationsResolvedByCleanRetest':nav,'initialHarnessFailuresRetained':initial_failures,'retestHistory':attempts,'reports':[{'path':name,'originalReportPassed':r.get('passed'),'checks':len(r['checks']),'sourceAndBuildUnchanged':r.get('sourceAndBuildUnchangedDuringRun')} for name,r in reports],'sourceAndBuildStableAcrossAllReportsAndNow':current_stable,'frozenIndexSHA256':hashlib.sha256((ROOT/'dist/index.html').read_bytes()).hexdigest(),'before56CapturesAndMetadataUnchanged':before_stable,'protectedFixtureProvenancePassed':provenance['passed'],'sourceAndBuildSHA256':current_hashes,'actualPracticeEvidence':threeD,'checks':final_checks}
summary['servedIndexSHA256']=hashlib.sha256(urlopen('http://127.0.0.1:5451',timeout=10).read()).hexdigest()
summary['servedIndexMatchesFrozenBuild']=summary['servedIndexSHA256']==summary['frozenIndexSHA256']=='c462802a6f4b51b37cd043b678c44a501943649cf47d5ebdcd841ceb49f7b3d8'
summary['passed']=summary['servedIndexMatchesFrozenBuild'] and all(c['passed'] is True for c in final_checks) and not any(errors.values()) and current_stable and before_stable and provenance['passed']
(DIR/'final-browser-summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
# Pair the original 56 actual captures with equivalent final regions. The added
# Home group has separate complete captures because the baseline focused Featured.
regions=[('home','Featured products'),('catalog','Catalog header'),('quiz','Quiz page top'),('quiz-question','Quiz first question'),('compare-empty','Compare empty workspace'),('compare-selected','Compare selected workspace'),('practice','Practice studio')]
rows=[]
for engine in ['chromium','webkit']:
 for viewport in ['desktop','landscape','tablet','mobile']:
  folder='final-ui' if engine=='chromium' else 'final-ui-webkit'
  for region,label in regions:
   before=f'before/{engine}-{viewport}-{region}.png'
   after=f'final-home/{engine}-{viewport}-home.png' if region=='home' else f'{folder}/{engine}-{viewport}-'+('quiz-top' if region=='quiz' else region)+'.png'
   assert (DIR/before).is_file() and (DIR/after).is_file(),(before,after)
   rows.append({'engine':engine,'viewport':viewport,'region':region,'label':label,'before':before,'after':after})
(DIR/'screenshot-pairs.json').write_text(json.dumps({'baselineCommit':provenance['baselineCommit'],'pairs':rows,'actualCapturePairs':len(rows),'beforeCaptureCount':56,'newHomeGroupCaptures':[f'final-home/{e}-{v}-home-features-complete.png' for e in ['chromium','webkit'] for v in ['desktop','landscape','tablet','mobile','portrait-edge']]},ensure_ascii=False,indent=2)+'\n')
html='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Fretline actual final UI screenshots</title><style>body{font:15px/1.55 system-ui;margin:32px;background:#111;color:#eee}a{color:#e4c47b}select{font:inherit;padding:8px;margin:5px}article{margin:28px 0}figure{margin:0}figure img{width:100%;height:auto;border:1px solid #555}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}h2{font-size:19px}figcaption{padding:6px 0;color:#ccc}@media(max-width:700px){.pair{grid-template-columns:1fr}}</style><h1>Actual final UI screenshots</h1><p>Chromium 154 and Linux WebKit 26.5; desktop 1440×1000, landscape 1194×834, portrait 768×1024, mobile 390×844. These are actual browser captures. No physical iPad Safari certification.</p><p>Baseline source: 985d0c4. The 56 baseline captures remain unchanged. Home pairs focus the retained Featured rail; the added Practice / restored Find / restored Compare group is shown separately below.</p><label>Engine <select id="engine"><option value="">Both</option><option>chromium</option><option>webkit</option></select></label><label>Viewport <select id="viewport"><option value="">All</option><option>desktop</option><option>landscape</option><option>tablet</option><option>mobile</option></select></label><div id="pairs">'''
for row in rows:
 html+=f'<article data-engine="{row["engine"]}" data-viewport="{row["viewport"]}"><h2>{row["engine"]} · {row["viewport"]} · {row["label"]}</h2><div class="pair"><figure><a href="{row["before"]}"><img loading="lazy" src="{row["before"]}"></a><figcaption>Before · 985d0c4</figcaption></figure><figure><a href="{row["after"]}"><img loading="lazy" src="{row["after"]}"></a><figcaption>After · frozen final build</figcaption></figure></div></article>'
html+='</div><h1>Complete restored Home group</h1><p>Exactly three cards. The extra portrait edge is 1024×1366.</p>'
for engine in ['chromium','webkit']:
 for viewport in ['desktop','landscape','tablet','mobile','portrait-edge']:
  name=f'final-home/{engine}-{viewport}-home-features-complete.png';assert (DIR/name).is_file();html+=f'<article><h2>{engine} · {viewport}</h2><a href="{name}"><img loading="lazy" style="max-width:100%" src="{name}"></a></article>'
html+='''<script>for(const id of ['engine','viewport'])document.getElementById(id).addEventListener('change',()=>{let e=document.getElementById('engine').value,v=document.getElementById('viewport').value;for(const a of document.querySelectorAll('#pairs article'))a.hidden=!!((e&&a.dataset.engine!==e)||(v&&a.dataset.viewport!==v));});</script></html>'''
(DIR/'screenshot-index.html').write_text(html)
print(json.dumps({k:summary[k] for k in ['passed','finalDistinctChecks','passedChecks','uiPracticeHomeChecks','quizCompareChecks','sourceAndBuildStableAcrossAllReportsAndNow','frozenIndexSHA256','before56CapturesAndMetadataUnchanged']},indent=2))
print('Actual paired screenshot regions:',len(rows))
raise SystemExit(not summary['passed'])
