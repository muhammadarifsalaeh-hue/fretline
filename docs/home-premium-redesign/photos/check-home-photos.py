"""Decode actual Home assets and check their recorded provenance and proportions.

The license assertions are manual source observations, not inferred from a build.
"""
from pathlib import Path
from PIL import Image, ImageOps
import hashlib, json

ROOT = Path(__file__).resolve().parents[3]
DIR = Path(__file__).resolve().parent
manifest = json.loads((DIR / 'manifest.json').read_text())
checks = []

def check(name, condition):
    checks.append({'name': name, 'passed': bool(condition)})
    assert condition, name

check('Four acquired real photographic sources', len(manifest['newSources']) == 4)
variant_files = []
for record in manifest['newSources']:
    source = DIR / 'originals' / record['file']
    raw = source.read_bytes()
    image = ImageOps.exif_transpose(Image.open(source))
    check(record['key'] + ' retained source hash and dimensions',
          hashlib.sha256(raw).hexdigest() == record['originalSHA256'] and image.size == (record['sourceWidth'], record['sourceHeight']))
    check(record['key'] + ' license source and attribution present',
          all(record.get(k) for k in ['sourceUrl', 'author', 'license', 'licenseUrl', 'checkedOn', 'changes']))
    check(record['key'] + ' is never named-model evidence', record['productEvidence'] is False)
    for variant in record['variants']:
        file = ROOT / 'src/assets/home-discovery' / variant['file']
        data = file.read_bytes()
        with Image.open(file) as derivative:
            derivative.load()
            check(variant['file'] + ' decoded WebP hash dimensions size',
                  derivative.format == 'WEBP' and derivative.size == (variant['width'], variant['height']) and len(data) == variant['bytes'] and hashlib.sha256(data).hexdigest() == variant['sha256'])
            check(variant['file'] + ' preserves proportions without upscaling',
                  derivative.width <= image.width and derivative.height <= image.height and abs(derivative.height - derivative.width * image.height / image.width) <= 1)
            if image.mode == 'RGBA':
                check(variant['file'] + ' preserves publisher transparency', derivative.mode == 'RGBA' and derivative.getextrema()[-1][0] == 0)
        variant_files.append(file.name)

check('Nine actual runtime derivatives', len(variant_files) == 9)
check('No untracked runtime file lacks provenance', sorted(variant_files) == sorted(p.name for p in (ROOT / 'src/assets/home-discovery').glob('*.webp')))
check('All new variants combined below 400 KiB', manifest['runtimeBytes'] < 400 * 1024)
check('New module uses local assets and keeps generic category boundary',
      'productEvidence: false' in (ROOT / 'src/data/homeDiscoveryAssets.js').read_text() and '/src/assets/home-discovery/*.webp' in (ROOT / 'src/data/homeDiscoveryAssets.js').read_text())
report = {'passed': all(x['passed'] for x in checks), 'checks': checks,
          'count': len(checks), 'newRuntimeBytes': manifest['runtimeBytes'],
          'manualLicenseReview': 'Source/license pages actually read on 2026-10-27; see README and license-observations.json.',
          'modelDataModified': False, 'physicalIPadSafariTested': False}
(DIR / 'checks.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('PASS', len(checks), 'source/derivative checks;', manifest['runtimeBytes'], 'new runtime bytes')
