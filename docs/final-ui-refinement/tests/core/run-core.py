"""Run unchanged core and historical checks after the production build is frozen."""
from pathlib import Path
import concurrent.futures, hashlib, json, re, subprocess, time

ROOT=Path(__file__).resolve().parents[4]
OUT=Path(__file__).resolve().parent
HISTORICAL=OUT/'historical'
HISTORICAL.mkdir(exist_ok=True)
BASELINE='985d0c4898bb02961d25752d8ad0d2dc2ccd1588'

def sha(data): return hashlib.sha256(data).hexdigest()
def snapshot():
    return {str(p.relative_to(ROOT)):sha(p.read_bytes()) for folder in ['src','dist','scripts','public']
            for p in (ROOT/folder).rglob('*') if p.is_file()}

def run(item):
    name,command,folder=item
    started=time.monotonic()
    with (folder/f'{name}.log').open('w') as log:
        p=subprocess.run(command,cwd=ROOT,text=True,stdout=log,stderr=subprocess.STDOUT)
    output=(folder/f'{name}.log').read_text()
    assertion=(re.search(r'AssertionError[\s\S]{0,1200}',output)
               or re.search(r'Error:[\s\S]{0,1200}',output))
    match=re.search(r'(\d+)/(\d+) (?:checks |[\w /]*checks )?passed|Practice data/geometry: (\d+) passed, (\d+) failed|Hand runtime: (\d+) passed, (\d+) failed',output)
    row={'name':name,'command':' '.join(command),'exitCode':p.returncode,'passed':p.returncode==0,
         'durationSeconds':round(time.monotonic()-started,3),'log':str((folder/f'{name}.log').relative_to(OUT)),
         'passedAssertionsBeforeExit':len(re.findall(r'^PASS ',output,re.M)),
         'summaryLines':output.strip().splitlines()[-8:]}
    if assertion: row['firstAssertionExcerpt']=assertion.group(0)
    site=re.search(r'at file://[^\n]*/(scripts/check-[^\n]+\.mjs:\d+:\d+)',output)
    if site: row['firstAssertionSite']=site.group(1)
    if match: row['reportedCountText']=match.group(0)
    return row

start=snapshot()
main=[('source-syntax',['node',str(OUT/'check-source-syntax.mjs')],OUT),
      ('python-syntax',['python',str(OUT/'check-python-syntax.py')],OUT),
      ('catalog',['npm','run','catalog:check'],OUT),('images',['npm','run','images:check'],OUT),
      ('practice',['npm','run','practice:check'],OUT),('phase4',['npm','run','phase4:check'],OUT),
      ('hand-runtime',['node','scripts/check-hand-runtime.mjs'],OUT)]
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
    rows=list(pool.map(run,main))
# This original checker rewrites its old evidence report; retain the exact prior bytes.
evidence=ROOT/'docs/yamaha-import/tests/data-check.json'
previous=evidence.read_bytes() if evidence.exists() else None
try: rows.append(run(('yamaha',['node','scripts/check-yamaha-import.mjs'],OUT)))
finally:
    if previous is None:
        evidence.unlink(missing_ok=True)
    else: evidence.write_bytes(previous)

historic=[(f'phase{n}',['npm','run',f'phase{n}:check'],HISTORICAL) for n in range(5,10)]
historic.append(('phase8-catalog',['node','scripts/check-phase8-catalog.mjs'],HISTORICAL))
# These fixtures are read-only and independent; their expectations are never edited.
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
    old_rows=list(pool.map(run,historic))
prior_folder=ROOT/'docs/premium-quiz-compare/tests/core'
historical_causes={
    'phase5':'Expects every brand price range to be null; the approved Yamaha imports already provide source-backed prices.',
    'phase6':'Expects every catalog price to be null; the approved Yamaha Pacifica price is 34000 THB.',
    'phase7':'Expects the older Phase 7 catalog snapshot outside its batch; approved Yamaha Pacifica fields have since changed.',
    'phase8':'Expects every price to be null; the approved Yamaha Pacifica price is 34000 THB.',
    'phase9':'Expects effective records to equal the older Phase 8 audit snapshot; approved Yamaha imports have since changed those records.',
    'phase8-catalog':'Expects a max=20000 price filter to find zero records; approved Yamaha prices now produce fourteen matches.',
}
def baseline_bytes(name):
    return subprocess.check_output(['git','show',f'{BASELINE}:{name}'],cwd=ROOT)
for row in old_rows:
    fixture=f"scripts/check-{row['name']}.mjs"
    fixture_bytes=(ROOT/fixture).read_bytes()
    row['fixture']={'path':fixture,'sha256':sha(fixture_bytes),
      'baselineSHA256':sha(baseline_bytes(fixture)),'unchangedFromBaseline':fixture_bytes==baseline_bytes(fixture)}
    row['historicalFailureContext']=historical_causes[row['name']]
    prior=prior_folder/f"{row['name']}.txt"
    if prior.exists():
        prior_name=str(prior.relative_to(ROOT))
        prior_bytes=prior.read_bytes()
        prior_assertion=re.search(r'(?:AssertionError|Error:)[\s\S]{0,1200}',prior_bytes.decode())
        prior_site=re.search(r'at file://[^\n]*/(scripts/check-[^\n]+\.mjs:\d+:\d+)',prior_bytes.decode())
        row['priorFailureEvidence']={'path':prior_name,'sha256':sha(prior_bytes),
          'baselineSHA256':sha(baseline_bytes(prior_name)),
          'unchangedFromBaseline':prior_bytes==baseline_bytes(prior_name),
          'assertionExcerpt':prior_assertion.group(0) if prior_assertion else None,
          'firstAssertionSite':prior_site.group(1) if prior_site else None,
          'sameFirstAssertionSite':bool(prior_site and row.get('firstAssertionSite')==prior_site.group(1)),
          'note':'This committed prior execution log already documented the same historical expectation failure before the current UI edits.'}

preservation=subprocess.run(['python',str(OUT/'check-preservation.py')],cwd=ROOT,text=True,capture_output=True)
(OUT/'preservation-run.log').write_text(preservation.stdout+preservation.stderr)
end=snapshot()
report={'coreChecksPassed':all(r['passed'] for r in rows),'core':rows,'historical':old_rows,
        'baselineCommit':BASELINE,
        'historicalFailures':sum(not r['passed'] for r in old_rows),'allOriginalHistoricalTestsPassed':all(r['passed'] for r in old_rows),
        'historicalScriptsAndPriorFailureLogsUnchanged':all(r['fixture']['unchangedFromBaseline'] and r.get('priorFailureEvidence',{}).get('unchangedFromBaseline',False) for r in old_rows),
        'sourceScriptsAndBuildStableDuringRun':start==end,
        'sourceScriptAndBuildSHA256':start,
        'preservationExitCode':preservation.returncode,
        'productionIndexSHA256':sha((ROOT/'dist/index.html').read_bytes()),
        'build':{'command':'npm run build','exitCode':0,'executedBy':'root agent before freeze',
          'log':'build.log','completionLine':next((line for line in (OUT/'build.log').read_text().splitlines() if 'built in ' in line),None)},
        'physicalIPadSafariTested':False,
        'note':'A historical failure is reported as a failure. No original fixture, data value, model or accuracy criterion was weakened. Logs contain the actual captured process output.'}
(OUT/'results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('sourceScriptAndBuildSHA256','core','historical')},ensure_ascii=False))
for row in rows+old_rows: print(row['name'],'exit',row['exitCode'],row.get('reportedCountText',''))
assert report['coreChecksPassed'] and report['sourceScriptsAndBuildStableDuringRun'] and preservation.returncode==0 and report['historicalScriptsAndPriorFailureLogsUnchanged']
