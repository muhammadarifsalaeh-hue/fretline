"""Git-bound preservation check; approved Compare caption deletion is explicit."""
from pathlib import Path
import hashlib, json, subprocess

ROOT = Path(__file__).resolve().parents[3]
DIR = Path(__file__).resolve().parent
baseline = json.loads((DIR / 'before/preservation-baseline.json').read_text())
hashes = baseline['protectedSHA256']
protected = hashes
changed = [path for path, digest in protected.items()
           if not (ROOT / path).is_file() or hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != digest]
report = {
    'baselineCommit': baseline['baselineCommit'],
    'protectedByteIdenticalFiles': len(protected),
    'changedProtectedFiles': changed,
    'standaloneQuizAndCompareByteIdentical': True if not changed else False,
    'passed': not changed,
}
(DIR / 'preservation.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print(json.dumps(report, ensure_ascii=False))
assert report['passed'], report
