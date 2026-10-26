"""Actual rendering/regression evidence for the selected current repaired hand candidates.

This does not certify a hand anatomically. All unapproved poses must stay hidden
until explicitly inspected with the warning. Applied joint/root fingerprints
are compared with the exact saved rotations, not merely distinct chord labels.
"""
from pathlib import Path
from io import BytesIO
import argparse
import hashlib
import json
import traceback

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--chords', required=True)
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
CANVAS = 'canvas[data-practice-canvas]'
CHORDS = args.chords.split(',')
assert CHORDS and len(CHORDS) == len(set(CHORDS))
PRESETS = ['angle', 'side', 'back', 'player']
library_file = ROOT / 'src/features/practice/assets/hand-poses.json'
library = json.loads(library_file.read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_snapshot():
    return {file.name: digest(file) for pattern in ['PracticePage-*.js', 'PracticePage-*.css',
            'practice-three-*.js', 'hand-poses-*.json', 'makehuman-left-arm.metadata-*.json',
            'makehuman-left-arm-sleeved-*.glb'] for file in (ROOT / 'dist/assets').glob(pattern)}


start = build_snapshot()
report = {'scope': 'Current actual repaired candidate renderings and controls; not anatomical hand approval',
          'url': args.url, 'chords': CHORDS, 'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'networkErrors': [],
          'poseLibrarySHA256': digest(library_file), 'productionArtifactSHA256': start,
          'limitations': ['Linux WebKit is not physical iPadOS Safari.',
                         'Candidates remain needs-review. Images establish actual rendering, not correctness of anatomy/contact.']}


def read(page):
    return page.locator(CANVAS).evaluate('''c => ({
      chord:c.dataset.handChordId, status:c.dataset.handStatus, visible:c.dataset.handVisible,
      review:c.dataset.handReviewMode, signature:c.dataset.handPoseSignature,
      asset:c.dataset.handModelSha256, camera:JSON.parse(c.dataset.camera),
      geometry:JSON.parse(c.dataset.practiceProjection).geometrySignature,
      stringPose:c.dataset.stringPose
    })''')


def settle(page):
    page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')


def pixels(canvas):
    return Image.open(BytesIO(canvas.screenshot(timeout=60000))).convert('RGB')


def same_camera(first, second):
    return all(abs(x-y) < 2e-5 for key in ['position', 'target', 'up'] for x, y in zip(first[key], second[key]))


def source_fingerprint(page, record):
    # Same Float32 normalization and word hash as the actual scene diagnostics;
    # calculate from independently supplied source TRS in the browser's number
    # format, then compare against the real applied Object3D/Bone values.
    return page.evaluate('''record => {
      const normalize = q => { const scale=1/Math.sqrt(q[0]*q[0]+q[1]*q[1]+q[2]*q[2]+q[3]*q[3]); return q.map(v=>v*scale); };
      const values=[...record.root.positionMm,...normalize(record.root.quaternion)];
      Object.keys(record.bones).sort((a,b)=>a.localeCompare(b)).forEach(name=>values.push(...normalize(record.bones[name].quaternion)));
      let h=2166136261;
      for (const word of new Uint32Array(new Float32Array(values).buffer)) h=Math.imul(h^word,16777619)>>>0;
      return h.toString(16).padStart(8,'0');
    }''', record)


with sync_playwright() as playwright:
    for engine in ['chromium', 'webkit']:
        browser = None
        try:
            browser = (playwright.chromium.launch(executable_path='/usr/bin/chromium',
                       args=['--no-sandbox', '--use-angle=swiftshader', '--enable-unsafe-swiftshader'])
                       if engine == 'chromium' else playwright.webkit.launch())
            for label, width, height in [('desktop', 1440, 1000), ('mobile', 390, 844)]:
                context = browser.new_context(viewport={'width': width, 'height': height},
                                              has_touch=True, reduced_motion='reduce', locale='th-TH')
                try:
                    page = context.new_page()
                    page.on('console', lambda msg, engine=engine: report['consoleErrors'].append({'engine': engine, 'text': msg.text}) if msg.type == 'error' else None)
                    page.on('pageerror', lambda error, engine=engine: report['runtimeErrors'].append({'engine': engine, 'text': str(error)}))
                    page.on('requestfailed', lambda request, engine=engine: report['networkErrors'].append({'engine': engine, 'url': request.url, 'error': request.failure}))
                    page.on('response', lambda response, engine=engine: report['networkErrors'].append({'engine': engine, 'url': response.url, 'status': response.status}) if response.status >= 400 else None)
                    page.goto(args.url.rstrip('/') + '/practice?chord=' + CHORDS[0], wait_until='networkidle')
                    canvas = page.locator(CANVAS)
                    expect(canvas).to_have_attribute('data-hand-asset-status', 'ready', timeout=60000)
                    page.evaluate('document.fonts.ready')
                    rows = []
                    previous_signature = None
                    for chord in CHORDS:
                        page.locator('[data-practice-chord="' + chord + '"]').tap()
                        expect(canvas).to_have_attribute('data-hand-chord-id', chord)
                        initial = read(page)
                        assert initial['status'] == 'needs-review' and initial['visible'] == 'false' and initial['review'] == 'false'
                        assert initial['asset'] == library['assetSha256']
                        expected = source_fingerprint(page, library['poses'][chord])
                        assert initial['signature'] == expected, {'chord': chord, 'actual': initial['signature'], 'expected': expected}
                        if previous_signature is not None:
                            assert initial['signature'] != previous_signature, 'Changing chord must apply a genuinely different real rig pose'
                        previous_signature = initial['signature']
                        page.locator('[data-camera-preset="angle"]').tap()
                        canvas.scroll_into_view_if_needed()
                        settle(page)
                        hidden_pixels = pixels(canvas)
                        page.locator('[data-practice-hand-review]').tap()
                        expect(page.locator('[data-hand-review-warning]')).to_be_visible()
                        settle(page)
                        visible = read(page)
                        assert visible['visible'] == 'true' and visible['review'] == 'true' and visible['status'] == 'needs-review'
                        assert visible['signature'] == expected and visible['stringPose'] == chord
                        shown_pixels = pixels(canvas)
                        count = sum(max(pixel) > 3 for pixel in ImageChops.difference(hidden_pixels, shown_pixels).get_flattened_data())
                        assert count > 100, ('Hand visibility must change real WebGL pixels', count)
                        angles = []
                        for preset in PRESETS:
                            page.locator('[data-camera-preset="' + preset + '"]').tap()
                            settle(page)
                            state = read(page)
                            assert state['signature'] == expected and state['geometry'] == visible['geometry'], 'Camera movement must not mutate fingers or strings'
                            name = f'UNAPPROVED-{engine}-{label}-{chord}-{preset}.png'
                            canvas.screenshot(path=str(args.output / name), timeout=60000)
                            angles.append({'preset': preset, 'camera': state['camera'], 'screenshot': name})
                        page.locator('.practice-canvas-stage').screenshot(path=str(args.output / f'UNAPPROVED-{engine}-{label}-{chord}-warning.png'), timeout=60000)
                        page.get_by_role('button', name='ซูมเข้า', exact=True).tap()
                        settle(page)
                        zoomed = read(page)
                        assert zoomed['camera']['distance'] < angles[-1]['camera']['distance']
                        page.get_by_role('button', name='รีเซ็ตกล้อง', exact=True).tap()
                        settle(page)
                        assert same_camera(read(page)['camera'], angles[0]['camera'])
                        assert read(page)['signature'] == expected
                        rows.append({'chord': chord, 'actualAppliedRigSignature': expected, 'changedWebGLPixels': count,
                                     'warningVisible': True, 'angles': angles, 'zoomAndReset': True,
                                     'anatomicalApproval': False})
                        # Leave the prototype open; selecting the next chord
                        # must close it. Close explicitly only on the last row.
                    page.locator('[data-practice-hand-review]').tap()
                    expect(canvas).to_have_attribute('data-hand-visible', 'false')
                    expect(page.locator('[data-hand-review-warning]')).to_have_count(0)
                    # The canonical trainer suite separately captures all four
                    # C views. Bind its newly authored pose to the actual rig as
                    # well, without adding a second screenshot loop here.
                    page.locator('[data-practice-chord="C"]').tap()
                    expect(canvas).to_have_attribute('data-hand-chord-id', 'C')
                    actual_c = read(page)
                    assert actual_c['signature'] == source_fingerprint(page, library['poses']['C'])
                    report['checks'].append({'engine': engine, 'browserVersion': browser.version,
                                             'viewport': [width, height], 'passed': True, 'poses': rows,
                                             'sourceCActualRigSignature': actual_c['signature']})
                    print('PASS', engine, label, ','.join(CHORDS) + ' actual source transforms, warning, four views, selection, zoom/reset', flush=True)
                finally:
                    context.close()
        except Exception:
            failure = traceback.format_exc()
            report['checks'].append({'engine': engine, 'passed': False, 'failure': failure})
            print('FAIL', engine, failure, flush=True)
        finally:
            if browser:
                browser.close()

report['buildArtifactsUnchangedDuringRun'] = start == build_snapshot() and report['poseLibrarySHA256'] == digest(library_file)
report['passed'] = len(report['checks']) == 4 and all(row['passed'] for row in report['checks']) and report['buildArtifactsUnchangedDuringRun'] and not any(report[key] for key in ['consoleErrors', 'runtimeErrors', 'networkErrors'])
(args.output / 'batch-poses-browser.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
raise SystemExit(0 if report['passed'] else 1)
