"""Summarize completed evidence only; never infer passes from script existence."""
from pathlib import Path
import hashlib, json

DIR = Path(__file__).resolve().parent
ROOT = DIR.parents[2]
home = json.loads((DIR / 'final/browser-results.json').read_text())
standalone = json.loads((DIR / 'standalone-regression/browser-results.json').read_text())
capture = json.loads((DIR.parent / 'screenshots/capture-results.json').read_text())
preservation = json.loads((DIR / 'preservation.json').read_text())
assert all(r['passed'] for r in [home, standalone, capture, preservation])
assert len(home['checks']) == 44 and len(standalone['checks']) == 25
assert all(r['sourceAndBuildUnchangedDuringRun'] for r in [home, standalone, capture])
common = set(home['sourceAndBuildSHA256']) & set(standalone['sourceAndBuildSHA256']) & set(capture['sourceAndBuildSHA256'])
changed = [name for name in common if len({r['sourceAndBuildSHA256'][name] for r in [home, standalone, capture]}) != 1
           or hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != home['sourceAndBuildSHA256'][name]]
assert not changed, changed
summary = {
    'passed': True, 'homeChecks': len(home['checks']), 'standaloneChecks': len(standalone['checks']),
    'deliveryScreenshots': len(capture['screenshots']), 'commonSourceAndBuildFiles': len(common),
    'allCommonHashesMatchCurrentFiles': not changed,
    'distIndexSHA256': hashlib.sha256((ROOT / 'dist/index.html').read_bytes()).hexdigest(),
    'browserVersions': home['browserVersions'], 'physicalIPadSafariTested': False,
    'homeErrorCounts': {key: len(home[key]) for key in ['consoleErrors','runtimeErrors','networkErrors','failedRequests']},
    'standaloneErrorCounts': {key: len(standalone[key]) for key in ['consoleErrors','runtimeErrors','networkErrors','failedRequests']},
}
(DIR / 'frozen-build-parity.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2)+'\n')
print(json.dumps(summary,ensure_ascii=False))
