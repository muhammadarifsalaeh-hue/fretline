"""Offline audit of Phase C assets, recorded reuse bases and unchanged products.

Checks existing local evidence; does not fetch pages or independently grant image
permission. No browser/npm/network calls, asset rewriting or catalogue edits.
"""
from collections import Counter
from datetime import date
from hashlib import sha256
from pathlib import Path
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree as ET
import ast
import json
import re
import traceback

ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).resolve().parents[1]
EXPECTED_BRANDS = {'yamaha', 'fender', 'gibson', 'taylor', 'ibanez', 'prs', 'epiphone', 'martin', 'squier'}
REPORT = {'method': 'Offline file/hash/recorded-evidence audit; no live source retrieval in this test.',
          'checks': [], 'assets': [], 'productFiles': [],
          'limitations': ['Recorded copyright/reuse evidence is not a manufacturer endorsement or trademark license.',
                          'This test checks stored evidence consistency, not current availability or legal correctness of external pages.']}


def check(name, condition, details=None):
    REPORT['checks'].append({'name': name, 'passed': bool(condition), 'details': details})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    return bool(condition)


def local_path(relative):
    path = (ROOT / relative).resolve()
    if ROOT not in path.parents:
        raise ValueError('Asset path escapes repository: ' + relative)
    return path


def https_url(value, hostname=None):
    parsed = urlparse(value or '')
    return parsed.scheme == 'https' and bool(parsed.hostname) and (not hostname or parsed.hostname == hostname)


def canonical_url(value):
    return unquote(value or '').replace(' ', '_')


def attribution_key(value):
    return re.sub(r'[^\w]', '', value.lower().replace('www.', ''), flags=re.UNICODE)


def read_js_object(source, name):
    """Read only the registry's literal source-credit tables, never execute JS."""
    match = re.search(r'const\s+' + re.escape(name) + r'\s*=\s*(\{.*?\n\});', source, re.S)
    if not match:
        raise ValueError('Registry literal needs review: ' + name)
    quoted = re.sub(r'([,{]\s*)([a-z][a-z0-9_]*):', r"\1'\2':", match.group(1))
    return ast.literal_eval(quoted)


def svg_audit(path):
    data = path.read_bytes()
    # ElementTree does not fetch the source files' external SVG DTDs. Reject any
    # internal entity declarations before parsing to avoid entity expansion.
    assert not re.search(br'<!ENTITY\s', data, re.I), 'SVG declares an XML entity'
    root = ET.fromstring(data)
    local = lambda name: name.rsplit('}', 1)[-1].lower()
    assert local(root.tag) == 'svg', 'Root is not SVG'
    assert root.get('viewBox') or root.get('width') and root.get('height'), 'Missing SVG bounds'
    forbidden = []
    geometry = Counter()
    for node in root.iter():
        tag = local(node.tag)
        if tag in {'script', 'foreignobject'}:
            forbidden.append({'tag': tag})
        if tag in {'path', 'polygon', 'polyline', 'circle', 'ellipse', 'rect', 'line', 'text', 'use'}:
            geometry[tag] += 1
        for attr, value in node.attrib.items():
            name = local(attr)
            if name.startswith('on'):
                forbidden.append({'tag': tag, 'attribute': name})
            if name == 'href' and value and not value.startswith('#'):
                forbidden.append({'tag': tag, 'externalHref': value})
            for target in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', value, re.I):
                if not target.startswith('#'):
                    forbidden.append({'tag': tag, 'externalURL': target})
        if tag == 'style':
            text = node.text or ''
            if re.search(r'@import|javascript:', text, re.I):
                forbidden.append({'tag': tag, 'style': 'import or script URL'})
            for target in re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', text, re.I):
                if not target.startswith('#'):
                    forbidden.append({'tag': tag, 'externalURL': target})
    assert not forbidden, forbidden
    assert geometry, 'No visible logo geometry found'
    return {'xmlParsed': True, 'scriptForeignObjectExternalHref': 0,
            'geometryElements': dict(geometry), 'viewBox': root.get('viewBox')}


def assets():
    manifest = json.loads((OUT / 'asset-downloads.json').read_text())
    logo_evidence = json.loads((OUT / 'assets-research/brand-logos.json').read_text())
    photo_evidence = json.loads((OUT / 'assets-research/brand-photographs.json').read_text())
    photo_notes = (OUT / 'photo-research/README.md').read_text()
    registry = (ROOT / 'src/data/homeBrandAssets.js').read_text()
    photo_credits = read_js_object(registry, 'photoCredits')
    logo_sources = read_js_object(registry, 'logoFiles')
    logos = [row for row in manifest if row.get('kind') == 'logo']
    photos = [row for row in manifest if row.get('kind') == 'photo']
    pairs = [(row.get('kind'), row.get('brand')) for row in manifest]
    check('Exactly eighteen unique registered files: nine logos and nine photos',
          len(manifest) == len(set(row['file'] for row in manifest)) == len(set(pairs)) == 18
          and len(logos) == len(photos) == 9, {'rows': len(manifest), 'kinds': dict(Counter(row['kind'] for row in manifest))})
    check('Same nine known brands have logo/photo assets; Córdoba intentionally excluded',
          {row['brand'] for row in logos} == {row['brand'] for row in photos} == EXPECTED_BRANDS)
    actual = {str(path.relative_to(ROOT)) for path in (ROOT / 'src/assets/home-brands').rglob('*') if path.suffix in {'.svg', '.png', '.webp'}}
    check('Every local Homepage asset is covered by the download/hash manifest',
          actual == {row['file'] for row in manifest}, {'unregistered': sorted(actual - {row['file'] for row in manifest})})
    selected_logos = {row['brandId']: row for row in logo_evidence['logos'] if row.get('status') == 'copyright-basis-recorded'}
    check('Nine logo source pages and recorded copyright bases exist in research JSON',
          set(selected_logos) == EXPECTED_BRANDS and all(
              https_url(row.get('sourcePage'), 'commons.wikimedia.org') and row.get('copyrightBasis')
              and row.get('trademarkNotice') is True for row in selected_logos.values()))
    cordoba = [row for row in logo_evidence['logos'] if row.get('brandId') == 'cordoba']
    check('Córdoba exclusion is explicit; no synthetic replacement is registered',
          len(cordoba) == 1 and cordoba[0].get('status') == 'use-existing-text-fallback'
          and 'cordoba' not in photo_credits and 'cordoba' not in logo_sources
          and photo_evidence.get('cordoba', {}).get('status') == 'no-qualified-photograph-selected')
    check('Source-credit registry has exactly the same nine logo/photo brands',
          set(photo_credits) == set(logo_sources) == EXPECTED_BRANDS)
    for row in manifest:
        label = row['kind'] + ':' + row['brand']
        item = {'kind': row['kind'], 'brand': row['brand'], 'file': row['file']}
        try:
            path = local_path(row['file'])
            blob = path.read_bytes()
            digest = sha256(blob).hexdigest()
            item.update({'actualSha256': digest, 'actualBytes': len(blob)})
            check(label + ' matches exact registered SHA-256 and byte count',
                  digest == row.get('sha256') and len(blob) == row.get('bytes'), item)
            check(label + ' records HTTPS original URL, original digest and access date',
                  https_url(row.get('downloadURL'), 'upload.wikimedia.org')
                  and bool(re.fullmatch(r'[a-f0-9]{64}', row.get('originalSha256', '')))
                  and date.fromisoformat(row['accessedOn']) is not None)
            if row['kind'] == 'logo':
                evidence = selected_logos[row['brand']]
                expected_source = 'https://commons.wikimedia.org/wiki/File:' + logo_sources[row['brand']]
                check(label + ' download and credit source match researched logo identity',
                      canonical_url(row['downloadURL']) == canonical_url(evidence.get('downloadUrl'))
                      and canonical_url(expected_source) == canonical_url(evidence.get('sourcePage')))
                if path.suffix == '.svg':
                    item['svg'] = svg_audit(path)
                    check(label + ' parses as SVG without script, foreignObject or external href', True, item['svg'])
                else:
                    check(label + ' is the selected transparent PNG, without silent SVG substitution',
                          row['brand'] == 'squier' and path.suffix == '.png'
                          and blob.startswith(b'\x89PNG\r\n\x1a\n'))
                changed = row['sha256'] != row['originalSha256']
                check(label + ' any file transformation has an explicit manifest note',
                      not changed or bool(row.get('changes')))
                if row['brand'] == 'yamaha':
                    note = row.get('changes', '')
                    check('Yamaha unsupported Adobe foreignObject removal is explicitly recorded',
                          changed and 'Adobe' in note and 'foreignObject' in note
                          and 'visible logo paths and geometry unchanged' in note, {'changes': note})
                    item['cleanup'] = {'originalSha256': row['originalSha256'], 'changes': note,
                                       'note': 'Safety/content structure checked locally; original geometry comparison is not performed by this offline test.'}
            else:
                credit = photo_credits[row['brand']]
                expected_source = 'https://commons.wikimedia.org/wiki/File:' + credit[0]
                license_match = re.fullmatch(r'CC BY(-SA)? (\d\.\d)', row.get('license', ''))
                check(label + ' has explicit source/author/license/transform/use records',
                      https_url(row.get('source'), 'commons.wikimedia.org') and bool(row.get('author'))
                      and bool(license_match) and bool(row.get('changes'))
                      and 'not assigned to a catalog model' in row.get('usage', ''),
                      {key: row.get(key) for key in ['source', 'author', 'license', 'changes', 'usage']})
                check(label + ' credit registry matches selected source and license',
                      canonical_url(row['source']) == canonical_url(expected_source)
                      and row['license'] == credit[2]
                      and attribution_key(row['author']) == attribution_key(credit[1])
                      and credit[3] == ('by-sa/' if license_match and license_match.group(1) else 'by/') + row['license'].rsplit(' ', 1)[1])
                # Research JSON contains earlier alternatives too. Require an
                # exact selected URL/license in JSON or in the accessed research
                # notes, rather than approving a different photo of this brand.
                json_match = any(canonical_url(candidate.get('sourcePage')) == canonical_url(row['source'])
                                 and candidate.get('license') == row['license'] and candidate.get('licenseEvidence')
                                 for candidate in photo_evidence['photographs'])
                markdown_match = canonical_url(row['source']) in canonical_url(photo_notes) and row['license'] in photo_notes
                check(label + ' exact selected source has recorded research evidence',
                      json_match or markdown_match, {'evidence': 'research JSON' if json_match else 'accessed photo-research README' if markdown_match else None})
                item['evidenceFormat'] = 'research JSON' if json_match else 'accessed photo-research README' if markdown_match else None
                check(label + ' is a local optimized WebP derivative',
                      path.suffix == '.webp' and blob.startswith(b'RIFF') and blob[8:12] == b'WEBP')
            REPORT['assets'].append(item)
        except Exception:
            failure = traceback.format_exc()
            check(label + ' asset audit completes', False, failure)
            item['failure'] = failure
            REPORT['assets'].append(item)
    # Source evidence is recorded, not promoted into product verification.
    REPORT['assetSummary'] = {'logos': len(logos), 'brandPhotos': len(photos),
                              'newProductPhotos': 0, 'cordoba': 'Existing text/neutral background fallback',
                              'trademarkNotice': 'Brand marks identify their owners; no endorsement is claimed.'}


def products():
    baseline_path = ROOT / 'docs/signature-redesign/phase-b/data-image-integrity.json'
    baseline = json.loads(baseline_path.read_text())
    snapshots = baseline['files']
    check('Phase B product-data/image baseline contains twenty-five unique files',
          len(snapshots) == len({item['path'] for item in snapshots}) == 25)
    rows = []
    for item in snapshots:
        path = local_path(item['path'])
        blob = path.read_bytes() if path.is_file() else None
        digest = sha256(blob).hexdigest() if blob is not None else None
        expected_digest = item.get('afterSha256', item['sha256'])
        unchanged = digest == expected_digest and blob is not None and len(blob) == item['bytes']
        row = {'path': item['path'], 'sha256': expected_digest, 'bytes': item['bytes'],
               'afterSha256': digest, 'afterBytes': len(blob) if blob is not None else None,
               'unchanged': unchanged}
        rows.append(row)
        check('Existing product data/image unchanged: ' + item['path'], unchanged)
    REPORT['productFiles'] = rows
    return {'baseline': '0b187d0',
            'baselineEvidence': str(baseline_path.relative_to(ROOT)),
            'historicalSourceBaseline': baseline.get('baseline'),
            'comparedAgainst': 'Phase C working tree', 'files': rows,
            'allUnchanged': all(item['unchanged'] for item in rows),
            'newHomeBrandAssetsAreSeparate': True}


integrity = None
try:
    assets()
    integrity = products()
except Exception:
    REPORT['harnessFailure'] = traceback.format_exc()
    print(REPORT['harnessFailure'], flush=True)
finally:
    REPORT['passed'] = bool(REPORT['checks']) and all(row['passed'] for row in REPORT['checks']) and not REPORT.get('harnessFailure')
    (OUT / 'assets-check.json').write_text(json.dumps(REPORT, ensure_ascii=False, indent=2) + '\n')
    if integrity is not None:
        (OUT / 'data-image-integrity.json').write_text(json.dumps(integrity, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if REPORT['passed'] else 1)
