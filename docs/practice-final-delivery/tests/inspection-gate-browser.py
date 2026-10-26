"""All 42 actual inspector gates and corrected default/player camera evidence.

This observes the production WebGL canvas and React controls. It cannot approve
hand anatomy. The separate Node runtime tests exercise direct API refusals.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import math
import subprocess
import traceback

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
CANVAS = 'canvas[data-practice-canvas]'
REVIEW = '[data-practice-hand-review]'
LIBRARY = ROOT / 'src/features/practice/assets/hand-poses.json'
library = json.loads(LIBRARY.read_text())
chords = json.loads(subprocess.check_output(['node', '--input-type=module', '-e',
    "import{PRACTICE_CHORDS}from'./src/features/practice/data/chords.js';console.log(JSON.stringify(PRACTICE_CHORDS))"], cwd=ROOT))
assert len(chords) == len(library['poses']) == 42
allowed = {key for key, pose in library['poses'].items()
           if pose.get('status') in ['needs-review', 'verified']
           and pose.get('audit', {}).get('collisionPassed') is True
           and pose.get('audit', {}).get('contactPassed') is True}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def snapshot():
    return {path.name: sha(path) for pattern in ['PracticePage-*.js', 'PracticePage-*.css',
        'practice-three-*.js', 'hand-poses-*.json', 'makehuman-left-arm.metadata-*.json',
        'makehuman-left-arm-sleeved-*.glb'] for path in (ROOT / 'dist/assets').glob(pattern)}


def state(canvas):
    return canvas.evaluate('''c => ({
      chord:c.dataset.handChordId, visible:c.dataset.handVisible,
      review:c.dataset.handReviewMode, allowed:c.dataset.handInspectionAllowed,
      status:c.dataset.handStatus, signature:c.dataset.handPoseSignature,
      stringPose:c.dataset.stringPose, model:c.dataset.handModelSha256,
      camera:JSON.parse(c.dataset.camera), projection:JSON.parse(c.dataset.practiceProjection)
    })''')


def source_signature(page, record):
    return page.evaluate('''record => {
      const unit=q=>{const r=1/Math.sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3]);return q.map(v=>v*r);};
      const values=[...record.root.positionMm,...unit(record.root.quaternion)];
      Object.keys(record.bones).sort((a,b)=>a.localeCompare(b)).forEach(n=>values.push(...unit(record.bones[n].quaternion)));
      let hash=2166136261;
      for(const word of new Uint32Array(new Float32Array(values).buffer))hash=Math.imul(hash^word,16777619)>>>0;
      return hash.toString(16).padStart(8,'0');
    }''', record)


def settle(page):
    page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')


def pixels(canvas):
    return Image.open(BytesIO(canvas.screenshot(timeout=60000))).convert('RGB')


def changed(first, second):
    assert first.size == second.size
    return sum(max(value) > 3 for value in ImageChops.difference(first, second).get_flattened_data())


def validate_diagram(page, chord):
    diagram = page.locator('[data-practice-active-chord="' + chord['id'] + '"] svg[data-chord-diagram]')
    expect(diagram).to_be_visible()
    assert diagram.get_attribute('data-string-order') == '6,5,4,3,2,1'
    rows = diagram.locator('[data-chord-string]').evaluate_all('''nodes=>nodes.map(n=>({
      string:Number(n.dataset.string),fret:n.dataset.fret,finger:n.dataset.finger
    }))''')
    assert len(rows) == 6
    for index, row in enumerate(rows):
        assert row['string'] == 6 - index
        assert row['fret'] == ('mute' if chord['frets'][index] is None else str(chord['frets'][index]))
        assert row['finger'] == ('' if chord['fingers'][index] is None else str(chord['fingers'][index]))
    return rows


def validate_view(value):
    camera = value['camera']
    delta = [p - t for p, t in zip(camera['position'], camera['target'])]
    length = math.sqrt(sum(v * v for v in delta))
    assert delta[1] / length > .5, 'The selected eye must face the fingerboard rather than rear wood'
    projection = value['projection']
    strings = {row['number']: row for row in projection['strings']}
    assert strings[6]['ndc'][1] > strings[1]['ndc'][1], 'Low E must remain above high e'
    assert projection['headstock'][0] > projection['body'][0]
    assert projection['headstock'][1] > projection['body'][1]


start = snapshot()
report = {'scope': 'Actual all42 inspection gates and camera rendering, not anatomical approval',
          'sourceLibrarySHA256': sha(LIBRARY), 'productionArtifactSHA256': start,
          'sourceInspectionAllowed': sorted(allowed), 'checks': [],
          'consoleErrors': [], 'runtimeErrors': [], 'networkErrors': [],
          'physicalIPadSafariTested': False, 'teachingHandsApprovedByHarness': 0}
with sync_playwright() as playwright:
    for engine in ['chromium', 'webkit']:
        browser = None
        try:
            browser = (playwright.chromium.launch(executable_path='/usr/bin/chromium',
                args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
                if engine == 'chromium' else playwright.webkit.launch())
            context = browser.new_context(viewport={'width': 1024, 'height': 900},
                has_touch=True, reduced_motion='reduce', locale='th-TH')
            page = context.new_page()
            page.on('console', lambda msg, e=engine: report['consoleErrors'].append({'engine': e, 'text': msg.text}) if msg.type == 'error' else None)
            page.on('pageerror', lambda err, e=engine: report['runtimeErrors'].append({'engine': e, 'text': str(err)}))
            page.on('requestfailed', lambda req, e=engine: report['networkErrors'].append({'engine': e, 'url': req.url, 'error': req.failure}))
            page.on('response', lambda res, e=engine: report['networkErrors'].append({'engine': e, 'url': res.url, 'status': res.status}) if res.status >= 400 else None)
            page.goto(args.url.rstrip('/') + '/practice?chord=C', wait_until='networkidle')
            canvas = page.locator(CANVAS)
            expect(canvas).to_have_attribute('data-hand-asset-status', 'ready', timeout=60000)
            page.evaluate('document.fonts.ready')
            rows = []
            for chord in chords:
                key = chord['id']
                page.locator('[data-practice-chord="' + key + '"]').click()
                expect(canvas).to_have_attribute('data-hand-chord-id', key)
                actual = state(canvas)
                assert actual['model'] == library['assetSha256']
                expected_signature = source_signature(page, library['poses'][key])
                assert actual['signature'] == expected_signature, (key, actual['signature'], expected_signature)
                assert actual['visible'] == 'false' and actual['review'] == 'false'
                assert actual['allowed'] == ('true' if key in allowed else 'false')
                diagram = validate_diagram(page, chord)
                if key in allowed:
                    expect(page.locator(REVIEW)).to_have_count(1)
                    canvas.scroll_into_view_if_needed(); settle(page)
                    hidden = pixels(canvas)
                    page.locator(REVIEW).click()
                    expect(canvas).to_have_attribute('data-hand-visible', 'true')
                    expect(page.locator('[data-hand-review-warning]')).to_be_visible()
                    settle(page)
                    shown = state(canvas)
                    assert shown['signature'] == expected_signature and shown['stringPose'] == key
                    difference = changed(hidden, pixels(canvas))
                    assert difference > 100, (key, difference)
                    page.locator(REVIEW).click()
                    expect(canvas).to_have_attribute('data-hand-visible', 'false')
                    details = {'allowed': True, 'actualChangedPixels': difference}
                else:
                    expect(page.locator(REVIEW)).to_have_count(0)
                    expect(page.locator('[data-hand-review-warning]')).to_have_count(0)
                    assert actual['stringPose'] == 'open'
                    details = {'allowed': False, 'rejectedHandHidden': True, 'openStringFallback': True}
                rows.append({'chord': key, 'signature': expected_signature, 'diagram': diagram, **details})
                if len(rows) % 7 == 0:
                    print('PROGRESS', engine, 'inspector gate', str(len(rows)) + '/42', flush=True)
            assert len(rows) == 42 and sum(row['allowed'] for row in rows) == len(allowed)
            page.locator('[data-practice-chord="C"]').click()
            expect(canvas).to_have_attribute('data-hand-chord-id', 'C')
            page.locator(REVIEW).click()
            expect(page.locator('[data-hand-review-warning]')).to_be_visible()
            views = []
            for label, width, height in [('desktop', 1440, 1000), ('tablet', 1024, 1366), ('mobile', 390, 844)]:
                page.set_viewport_size({'width': width, 'height': height})
                for preset in ['angle', 'player']:
                    page.locator('[data-camera-preset="' + preset + '"]').click()
                    canvas.scroll_into_view_if_needed(); settle(page)
                    value = state(canvas)
                    validate_view(value)
                    assert value['signature'] == source_signature(page, library['poses']['C'])
                    name = f'UNAPPROVED-{engine}-{label}-C-{preset}.png'
                    canvas.screenshot(path=str(args.output / name), timeout=60000)
                    views.append({'viewport': [width, height], 'preset': preset, 'camera': value['camera'], 'screenshot': name})
            report['checks'].append({'engine': engine, 'browserVersion': browser.version,
                'passed': True, 'chordsChecked': 42, 'allowed': len(allowed), 'blocked': 42 - len(allowed),
                'sourceTransformsMatched': True, 'chords': rows, 'views': views})
            context.close()
            print('PASS', engine, 'all42 inspector gates and six actual default/player captures', flush=True)
        except Exception:
            failure = traceback.format_exc()
            report['checks'].append({'engine': engine, 'passed': False, 'failure': failure})
            print('FAIL', engine, failure, flush=True)
        finally:
            if browser:
                browser.close()
report['buildArtifactsUnchangedDuringRun'] = start == snapshot() and sha(LIBRARY) == report['sourceLibrarySHA256']
report['passed'] = (len(report['checks']) == 2 and all(row['passed'] for row in report['checks'])
    and report['buildArtifactsUnchangedDuringRun'] and not any(report[key] for key in ['consoleErrors', 'runtimeErrors', 'networkErrors']))
(args.output / 'inspection-gate-browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(not report['passed'])
