"""Lossless storage compression for NEW browser artifacts only.

ImageMagick encodes and compares pixels. Python only orchestrates files, hashes
and report references. Original raw JSON reports are preserved byte-for-byte in
gzip archives before changing screenshot filename references.
"""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from hashlib import sha256
import gzip, json, os, shutil, subprocess

DIR = Path(__file__).resolve().parent
FILES = sorted(DIR.rglob('*.png'))
if not FILES:
    assert (DIR / 'screenshot-optimization.json').is_file(), 'No captures or existing manifest found.'
    print('All existing screenshots are already stored as lossless WebP.')
    raise SystemExit(0)
groups = {}
for file in FILES:
    digest = sha256(file.read_bytes()).hexdigest()
    groups.setdefault(digest, []).append(file)
environment = dict(os.environ, MAGICK_THREAD_LIMIT='1')
def convert(item):
    digest, files = item
    first = files[0]
    target = first.with_suffix('.webp')
    subprocess.run(['magick', str(first), '-define', 'webp:lossless=true', '-define', 'webp:method=4', '-quality', '100', str(target)], check=True, env=environment, capture_output=True)
    compared = subprocess.run(['magick', 'compare', '-metric', 'AE', str(first), str(target), 'null:'], check=True, env=environment, capture_output=True, text=True)
    assert compared.stderr.strip() == '0', (str(first), compared.stderr)
    encoded = target.read_bytes()
    encoded_hash = sha256(encoded).hexdigest()
    rows = []
    for file in files:
        webp = file.with_suffix('.webp')
        if webp != target: webp.write_bytes(encoded)
        assert sha256(file.read_bytes()).hexdigest() == digest
        rows.append({'originalPNG': str(file.relative_to(DIR)), 'originalPNGBytes': file.stat().st_size, 'originalPNGSHA256': digest, 'losslessWebP': str(webp.relative_to(DIR)), 'losslessWebPBytes': len(encoded), 'losslessWebPSHA256': encoded_hash, 'absoluteErrorPixels': 0, 'validation': 'ImageMagick compare -metric AE = 0; byte-identical PNG inputs share this validated encoding'})
    return rows
records = []
with ThreadPoolExecutor(max_workers=4) as executor:
    pending = [executor.submit(convert, item) for item in groups.items()]
    for i, job in enumerate(as_completed(pending), 1):
        records.extend(job.result())
        if i % 10 == 0: print('Validated lossless groups', i, '/', len(pending), flush=True)
records.sort(key=lambda row: row['originalPNG'])
names = {Path(row['originalPNG']).name: Path(row['losslessWebP']).name for row in records}
fullnames = {row['originalPNG']: row['losslessWebP'] for row in records}
def update(value):
    if isinstance(value, str): return fullnames.get(value, names.get(value, value))
    if isinstance(value, list): return [update(x) for x in value]
    # Keys include source/build fingerprint paths and are never modified.
    if isinstance(value, dict): return {k: update(v) for k, v in value.items()}
    return value
archives = []
for file in sorted(DIR.rglob('*.json')):
    if file.name in ['screenshot-optimization.json', 'summary.json']: continue
    raw = file.read_bytes()
    parsed = json.loads(raw)
    changed = update(parsed)
    if changed == parsed: continue
    archived = DIR / 'raw-reports' / (str(file.relative_to(DIR)) + '.gz')
    archived.parent.mkdir(parents=True, exist_ok=True)
    archived.write_bytes(gzip.compress(raw, compresslevel=9, mtime=0))
    assert gzip.decompress(archived.read_bytes()) == raw
    archives.append({'deliveredJSON': str(file.relative_to(DIR)), 'originalRawJSONArchive': str(archived.relative_to(DIR)), 'originalRawJSONSHA256': sha256(raw).hexdigest(), 'onlyChanges': 'Screenshot filename references from .png to .webp; all assertions, results, error events, source/build fingerprint keys and values retained'})
    file.write_text(json.dumps(changed, ensure_ascii=False, indent=2) + '\n')
manifest = {'format': 'lossless WebP', 'pixelValidation': 'Every distinct original PNG SHA-256 group compared using ImageMagick AE and required exactly zero changed pixels.', 'screenshotCount': len(records), 'distinctPNGGroups': len(groups), 'originalPNGBytes': sum(x['originalPNGBytes'] for x in records), 'losslessWebPBytes': sum(x['losslessWebPBytes'] for x in records), 'records': records, 'rawReportArchives': archives, 'scope': 'Only new docs/homepage-visual-update/tests artifacts. No pre-existing docs, application code, product/editorial images, tests/assertions/results or source/build fingerprint paths changed.'}
manifest['uniqueOriginalPNGBytes'] = sum({r['originalPNGSHA256']: r['originalPNGBytes'] for r in records}.values())
manifest['uniqueLosslessWebPBytes'] = sum({r['losslessWebPSHA256']: r['losslessWebPBytes'] for r in records}.values())
manifest['distinctLosslessWebPGroups'] = len({r['losslessWebPSHA256'] for r in records})
(DIR / 'screenshot-optimization.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n')
for file in FILES:
    assert file.with_suffix('.webp').is_file()
    file.unlink()
cache = DIR / '__pycache__'
if cache.exists(): shutil.rmtree(cache)
print('LOSSLESS COMPLETE', len(records), 'screenshots;', manifest['originalPNGBytes'], '->', manifest['losslessWebPBytes'], 'bytes; every validated AE=0', flush=True)
