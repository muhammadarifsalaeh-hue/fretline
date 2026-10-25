"""Actual browser acceptance for the 42-chord trainer; no hand-pose approval.

Run only against an already-built preview. Expected voicings are an independent
fixture; actual SVG circles, grid lines, barre strokes and text are measured.
Fault cases alter only the named WebGL capability or actual lazy scene request.
"""
from pathlib import Path
from urllib.parse import parse_qs, urlparse
from io import BytesIO
import argparse
import hashlib
import json
import math
import re
import subprocess
import time
import traceback

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[3]
parser = argparse.ArgumentParser()
parser.add_argument('--url', required=True)
parser.add_argument('--engine', choices=['chromium', 'webkit'], required=True)
parser.add_argument('--output', type=Path, required=True)
parser.add_argument('--cases', default='')
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
BASE = args.url.rstrip('/')
def build_snapshot():
    assets = ROOT / 'dist/assets'
    return {file.name:hashlib.sha256(file.read_bytes()).hexdigest()
            for pattern in ['PracticePage-*.js','PracticePage-*.css','practice-three-*.js','hand-poses-*.json',
                            'makehuman-left-arm.metadata-*.json','makehuman-left-arm-sleeved-*.glb']
            for file in assets.glob(pattern)}


build_before = build_snapshot()
CANVAS = 'canvas[data-practice-canvas]'
STATUS = '[data-practice-status]'
SCENE = re.compile(r'.*/practice-three-[^/]+\.js(?:\?.*)?$')
HAND_MODEL = re.compile(r'.*/makehuman-left-arm-sleeved(?:-[^/]+)?\.glb(?:\?.*)?$')
HAND_RESOURCE = re.compile(r'.*/(?:makehuman-left-arm-sleeved(?:-[^/]+)?\.glb|makehuman-left-arm\.metadata(?:-[^/]+)?\.json|hand-poses(?:-[^/]+)?\.json)(?:\?.*)?$')
fixture = json.loads((Path(__file__).parent / 'reference-voicings.json').read_text())
expected = {key: {'frets': [None if fret == 'x' else int(fret) for fret in shape], 'type': group['type']}
            for group in fixture['groups'] for key, shape in group['voicings'].items()}
source = json.loads(subprocess.check_output(['node', '--input-type=module', '-e',
    "import {PRACTICE_CHORDS} from './src/features/practice/data/chords.js'; console.log(JSON.stringify(PRACTICE_CHORDS));"], cwd=ROOT))
data = {item['id']: item for item in source}
pose_path = ROOT / 'src/features/practice/assets/hand-poses.json'
pose_library = json.loads(pose_path.read_text()) if pose_path.exists() else {}
candidate_ids = {key for key, record in pose_library.get('poses', {}).items() if record.get('status') != 'unavailable'}
verified_ids = {key for key, record in pose_library.get('poses', {}).items()
                if record.get('status') == 'verified' and record.get('reviewed') is True
                and all(record.get('audit', {}).get(gate) is True
                        for gate in ['collisionPassed','contactPassed','anatomyPassed','multiViewReviewed'])}
assert not any(record.get('status') == 'verified' and key not in verified_ids
               for key, record in pose_library.get('poses', {}).items()), 'A verified source pose must have all independent review gates'
report = {'engine': args.engine, 'url': BASE, 'scope': '42-chord music/diagram/trainer acceptance; anatomical hand poses are assessed separately',
          'checks': [], 'consoleErrors': [], 'runtimeErrors': [], 'failedRequests': [], 'badResponses': [], 'warnings': [],
          'expectedFaultErrors': [], 'screenshots': [], 'sourceDataSHA256': hashlib.sha256((ROOT / 'src/features/practice/data/chords.js').read_bytes()).hexdigest(),
          'limitations': ['Actual Linux Chromium/WebKit engines, not physical iPadOS Safari.', 'Chromium uses real SwiftShader software WebGL2.',
                          'Structural musical/diagram approval does not establish anatomical hand contact, anatomy or visual fidelity.']}


def query(page):
    return parse_qs(urlparse(page.url).query)


def go(page, path='/practice', ready=True):
    page.goto(BASE + path, wait_until='networkidle' if ready else 'domcontentloaded')
    if ready:
        expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
        expect(page.locator(CANVAS)).to_be_visible()
    page.evaluate('document.fonts.ready')


def choose(page, chord_id, ready=True):
    button = page.locator('[data-practice-chord="' + chord_id + '"]')
    button.click()
    expect(button).to_have_attribute('aria-pressed', 'true')
    expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord', chord_id)
    if ready:
        expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', chord_id)
    assert query(page).get('chord') == [chord_id], page.url


def hand(page, ready=True):
    canvas = page.locator(CANVAS)
    if ready:
        expect(canvas).to_have_attribute('data-hand-asset-status', 'ready', timeout=45000)
    value = canvas.evaluate('''c => Object.fromEntries(['handStatus','handAssetStatus','handVisible','handModelReady',
      'handChordId','handReviewMode','handPoseSignature','handModelSha256'].map(key=>[key,c.dataset[key]]))''')
    assert value['handStatus'] in ['verified','needs-review','unavailable'], value
    assert value['handChordId'] == canvas.get_attribute('data-chord-id'), value
    if value['handAssetStatus'] == 'ready':
        assert re.fullmatch(r'[a-f0-9]{64}', value['handModelSha256']), value
        assert re.fullmatch(r'[a-f0-9]{8}', value['handPoseSignature']), value
        assert value['handModelReady'] == 'true'
    if value['handStatus'] != 'verified' and value['handReviewMode'] != 'true':
        assert value['handVisible'] == 'false', 'Unapproved hands must be hidden in the normal lesson'
    return value


def shot(page, name, canvas=False):
    target = args.output / (name + '.png')
    if canvas:
        page.locator(CANVAS).scroll_into_view_if_needed()
        page.locator(CANVAS).screenshot(path=str(target),timeout=60000)
    else:
        page.screenshot(path=str(target), full_page=True,timeout=60000)
    report['screenshots'].append(target.name)


def pitch_value(name):
    match = re.fullmatch(r'([A-G])([#b]?)(-?\d+)', name)
    assert match, name
    return (int(match[3]) + 1) * 12 + fixture['roots'][match[1]] + (1 if match[2] == '#' else -1 if match[2] == 'b' else 0)


def diagram(page, chord_id, compact=False):
    parent = page.locator('[data-practice-chord="' + chord_id + '"]' if compact else '[data-practice-active-chord="' + chord_id + '"]')
    svg = parent.locator('svg[data-chord-diagram="' + chord_id + '"]')
    expect(svg).to_be_visible()
    raw = svg.evaluate('''svg => {
      const line = e => ({x1:e.x1.baseVal.value,x2:e.x2.baseVal.value,y1:e.y1.baseVal.value,y2:e.y2.baseVal.value,stroke:Number(e.getAttribute('stroke-width')||1)});
      const box = svg.viewBox.baseVal;
      return {base:Number(svg.dataset.baseFret),order:svg.dataset.stringOrder,viewBox:{x:box.x,y:box.y,width:box.width,height:box.height},
        title:svg.querySelector('title')?.textContent||'',hidden:svg.getAttribute('aria-hidden'),role:svg.getAttribute('role'),
        vertical:[...svg.querySelectorAll('g[fill="none"] > line')].filter(e=>e.x1.baseVal.value===e.x2.baseVal.value).map(line),
        horizontal:[...svg.querySelectorAll('[data-fret-boundary]')].map(e=>({...line(e),boundary:Number(e.dataset.fretBoundary),nut:e.dataset.nut})),
        labels:[...svg.querySelectorAll('[data-fret-label]')].map(e=>({fret:Number(e.dataset.fretLabel),text:e.textContent})),
        strings:[...svg.querySelectorAll('[data-chord-string]')].map(e=>({string:Number(e.dataset.string),fret:e.dataset.fret,finger:e.dataset.finger,note:e.dataset.note,state:e.dataset.stringState,
          label:e.querySelector('.practice-diagram-string')?.textContent,
          circles:[...e.querySelectorAll('circle')].map(c=>({x:c.cx.baseVal.value,y:c.cy.baseVal.value,r:c.r.baseVal.value,dot:c.classList.contains('practice-diagram-dot')})),
          texts:[...e.querySelectorAll('text')].map(t=>({text:t.textContent,x:t.x.baseVal[0].value,y:t.y.baseVal[0].value,finger:t.classList.contains('practice-diagram-finger')}))})),
        barres:[...svg.querySelectorAll('[data-chord-barre]')].map(e=>({finger:Number(e.dataset.finger),fret:Number(e.dataset.fret),fromString:Number(e.dataset.fromString),toString:Number(e.dataset.toString),lines:[...e.querySelectorAll('line')].map(line)}))};
    }''')
    reference, chord = expected[chord_id], data[chord_id]
    frets = reference['frets']
    base = 1 if 0 in frets else min(fret for fret in frets if fret is not None and fret > 0)
    assert raw['base'] == base and raw['order'] == '6,5,4,3,2,1', raw
    assert len(raw['vertical']) == 6 and len(raw['horizontal']) == 6, raw
    xx = [line['x1'] for line in raw['vertical']]
    yy = [line['y1'] for line in raw['horizontal']]
    assert all(xx[index] < xx[index+1] for index in range(5))
    assert all(yy[index] < yy[index+1] for index in range(5))
    assert all(line['y1'] == yy[0] and line['y2'] == yy[-1] for line in raw['vertical'])
    assert [line['boundary'] for line in raw['horizontal']] == list(range(base-1, base+5))
    assert sum(line.get('nut') == 'true' for line in raw['horizontal']) == (1 if base == 1 else 0)
    assert [item['string'] for item in raw['strings']] == [6,5,4,3,2,1]
    assert [item['label'] for item in raw['strings']] == ['E','A','D','G','B','e']
    for index, (string, fret) in enumerate(zip(raw['strings'], frets)):
        state = 'muted' if fret is None else 'open' if fret == 0 else 'fretted'
        assert string['state'] == state and string['fret'] == ('mute' if fret is None else str(fret)), (chord_id, string)
        assert string['finger'] == (str(chord['fingers'][index]) if fret is not None and fret > 0 else '')
        if fret is None:
            assert not string['circles'] and string['note'] == ''
            assert any(text['text'] == '×' and text['x'] == xx[index] and text['y'] < yy[0] for text in string['texts'])
        else:
            assert pitch_value(string['note']) == fixture['tuningMidi'][index] + fret
            assert len(string['circles']) == 1
            circle = string['circles'][0]
            assert circle['x'] == xx[index]
            if fret == 0:
                assert not circle['dot'] and circle['y'] + circle['r'] < yy[0]
            else:
                assert circle['dot']
                offset = fret - base
                assert 0 <= offset < 5 and yy[offset] < circle['y'] < yy[offset+1], (chord_id, fret, raw)
                assert any(text['finger'] and text['text'] == str(chord['fingers'][index]) and text['x'] == circle['x'] and text['y'] == circle['y'] for text in string['texts'])
            assert raw['viewBox']['x'] <= circle['x'] - circle['r'] and circle['x'] + circle['r'] <= raw['viewBox']['width']
            assert raw['viewBox']['y'] <= circle['y'] - circle['r'] and circle['y'] + circle['r'] <= raw['viewBox']['height']
    assert len(raw['barres']) == len(chord['barres'])
    for actual, barre in zip(raw['barres'], chord['barres']):
        assert {key: actual[key] for key in ['finger','fret','fromString','toString']} == barre
        assert len(actual['lines']) == 1, 'Validated continuous barres must render a real connecting stroke'
        line = actual['lines'][0]
        assert line['x1'] == xx[6-barre['fromString']] and line['x2'] == xx[6-barre['toString']]
        offset = barre['fret'] - base
        assert yy[offset] < line['y1'] == line['y2'] < yy[offset+1] and line['stroke'] >= 8
        for string in range(barre['fromString'], barre['toString']-1, -1):
            assert frets[6-string] is not None and frets[6-string] >= barre['fret'], 'Visible barre must not block an open/muted/lower note'
    if compact:
        assert raw['hidden'] == 'true'
        if base > 1: assert any(label['fret'] == base and label['text'] == str(base) for label in raw['labels'])
    else:
        assert raw['role'] == 'img' and raw['title']
        assert [label['fret'] for label in raw['labels']] == list(range(base, base+5))
        for index, fret in enumerate(frets):
            descriptor = str(6-index) + ': ' + ('mute' if fret is None else 'open' if fret == 0 else 'fret ' + str(fret) + ', finger ' + str(chord['fingers'][index]))
            assert descriptor in raw['title'], (chord_id, descriptor, raw['title'])
    return {'chord': chord_id, 'compact': compact, 'baseFret': base, 'frets': frets, 'barres': raw['barres'], 'stringNotes': [string['note'] for string in raw['strings']]}


def all_chords(page):
    go(page)
    hand(page)
    assert len(expected) == 42
    expect(page.locator('[data-practice-chord]')).to_have_count(42)
    expect(page.locator('[data-practice-result-count]')).to_have_attribute('data-practice-result-count', '42')
    assert page.locator('[data-practice-chord]').evaluate_all('nodes=>nodes.map(n=>n.dataset.practiceChord)') == list(expected)
    page.evaluate('window.__trainerSentinel="same-document"')
    states = []
    for chord_id in expected:
        compact = diagram(page, chord_id, compact=True)
        choose(page, chord_id)
        full = diagram(page, chord_id)
        detail = page.locator('[data-practice-active-chord]')
        expect(detail.locator('[data-diagram-status]')).to_have_count(1)
        expect(detail.locator('[data-hand-pose-status]')).to_have_count(1)
        assert detail.locator('[data-diagram-status]').get_attribute('data-diagram-status') in ['verified','needs-review','unavailable']
        assert detail.locator('[data-hand-pose-status]').get_attribute('data-hand-pose-status') in ['verified','needs-review','unavailable']
        assert detail.locator('[data-finger-instruction]').count() == sum(fret is not None and fret > 0 for fret in expected[chord_id]['frets'])
        assert detail.locator('[data-barre-instruction]').count() == len(data[chord_id]['barres'])
        for instruction in detail.locator('[data-finger-instruction]').all():
            string = int(instruction.get_attribute('data-string'))
            fret = int(instruction.get_attribute('data-fret'))
            finger = int(instruction.get_attribute('data-finger-instruction'))
            assert expected[chord_id]['frets'][6-string] == fret and data[chord_id]['fingers'][6-string] == finger
            text = instruction.inner_text()
            assert str(string) in text and str(fret) in text and data[chord_id]['notes'][6-string] in text
        statuses = detail.locator('.practice-string-status dd').all_text_contents()
        assert len(statuses) == 2
        for text, target in zip(statuses, [0, None]):
            assert [int(number) for number in re.findall(r'\d+', text)] == [6-index for index,fret in enumerate(expected[chord_id]['frets']) if fret == target]
        assert page.evaluate('window.__trainerSentinel') == 'same-document'
        assert page.locator(CANVAS).count() == 1
        actual_hand = hand(page)
        assert actual_hand['handReviewMode'] == 'false'
        if chord_id in verified_ids:
            assert actual_hand['handStatus'] == 'verified' and actual_hand['handVisible'] == 'true', (chord_id, actual_hand)
        elif chord_id in candidate_ids:
            assert actual_hand['handStatus'] == 'needs-review', (chord_id, actual_hand)
        else:
            assert actual_hand['handStatus'] == 'unavailable' and actual_hand['handVisible'] == 'false', (chord_id, actual_hand)
        states.append({'full': full, 'compact': compact, 'diagramStatus': detail.locator('[data-diagram-status]').get_attribute('data-diagram-status'),
                       'handPoseStatus': detail.locator('[data-hand-pose-status]').get_attribute('data-hand-pose-status'), 'actualHand':actual_hand})
        if len(states) % 7 == 0:
            print('PROGRESS',args.engine,'rendered diagrams',str(len(states))+'/42',flush=True)
    fingerprints = {row['full']['chord']:row['actualHand']['handPoseSignature'] for row in states if row['full']['chord'] in candidate_ids}
    assert len(fingerprints) == len(candidate_ids)
    assert len(set(fingerprints.values())) == len(fingerprints), 'Different candidate chords must apply different actual bone/root transforms'
    (args.output / ('rendered-diagrams-'+args.engine+'.json')).write_text(json.dumps({
        'passed':True,'count':42,'diagrams':states,'actualCandidatePoseFingerprints':fingerprints,
        'sourceDataSHA256':report['sourceDataSHA256'],'anatomicalHandApproval':False},ensure_ascii=False,indent=2)+'\n')
    shot(page, 'all-42-library')
    return {'count': 42, 'diagrams': states, 'sameDocument': True, 'actualCandidatePoseFingerprints':fingerprints,'anatomicalHandApproval': False}


def filters(page):
    go(page)
    groups = []
    for group in fixture['groups']:
        page.locator('[data-practice-type="' + group['type'] + '"]').click()
        expect(page.locator('[data-practice-type="' + group['type'] + '"]')).to_have_attribute('aria-pressed', 'true')
        expect(page.locator('[data-practice-result-count]')).to_have_attribute('data-practice-result-count', '7')
        ids = page.locator('[data-practice-chord]').evaluate_all('nodes=>nodes.map(n=>n.dataset.practiceChord)')
        assert ids == list(group['voicings']), ids
        assert query(page).get('type') == [group['type']]
        groups.append({'type': group['type'], 'ids': ids})
    page.locator('[data-practice-type="all"]').click()
    search = page.locator('#practice-chord-search')
    search.fill('A')
    expect(page.locator('[data-practice-result-count]')).to_have_attribute('data-practice-result-count', '7')
    assert page.locator('[data-practice-chord]').evaluate_all('nodes=>nodes.map(n=>n.dataset.practiceChord)') == ['A','Am','A7','Amaj7','Am7','Asus2','Asus4']
    search.fill('bm7')
    expect(page.locator('[data-practice-chord]')).to_have_count(1)
    expect(page.locator('[data-practice-chord="Bm7"]')).to_be_visible()
    expect(page.locator('[data-practice-next]')).to_be_disabled()
    expect(page.locator('[data-practice-previous]')).to_be_disabled()
    assert query(page).get('q') == ['bm7']
    search.fill('minor 7th')
    expect(page.locator('[data-practice-result-count]')).to_have_attribute('data-practice-result-count', '7')
    assert page.locator('[data-practice-chord]').evaluate_all('nodes=>nodes.map(n=>n.dataset.practiceChord)') == list(fixture['groups'][4]['voicings'])
    search.fill('no-such-chord-xyz')
    expect(page.locator('[data-practice-chord]')).to_have_count(0)
    expect(page.locator('.practice-chord-empty')).to_be_visible()
    expect(page.locator('[data-practice-next]')).to_be_disabled()
    expect(page.locator('[data-practice-previous]')).to_be_disabled()
    expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord', 'C')
    search.fill('')
    expect(page.locator('[data-practice-chord]')).to_have_count(42)
    assert 'q' not in query(page) and 'type' not in query(page)
    return {'groups': groups, 'caseInsensitiveName': 'bm7', 'multiTermSearch': 'minor 7th', 'emptyResultsKeepSelection': True}


def navigation_history(page):
    go(page, '/practice?chord=F&type=major')
    page.evaluate('window.__trainerHistory="same-document"')
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'F')
    page.locator('[data-practice-next]').click()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'G')
    page.locator('[data-practice-previous]').click()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'F')
    page.go_back(wait_until='domcontentloaded')
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'G')
    page.go_forward(wait_until='domcontentloaded')
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'F')
    assert page.evaluate('window.__trainerHistory') == 'same-document'
    page.reload(wait_until='networkidle')
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'F')
    expect(page.locator('[data-practice-type="major"]')).to_have_attribute('aria-pressed', 'true')
    page.locator('[data-practice-type="minor"]').click()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'F')
    page.locator('[data-practice-next]').click()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Cm')
    page.locator('[data-practice-previous]').click()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Bm')
    page.locator('[data-practice-chord="Am"]').focus()
    page.keyboard.press('ArrowRight')
    expect(page.locator('[data-practice-chord="Bm"]')).to_be_focused()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Bm')
    page.keyboard.press('Home')
    expect(page.locator('[data-practice-chord="Cm"]')).to_be_focused()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Cm')
    page.keyboard.press('End')
    expect(page.locator('[data-practice-chord="Bm"]')).to_be_focused()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Bm')
    assert query(page).get('chord') == ['Bm'] and query(page).get('type') == ['minor']
    return {'sharedURLAndReload': 'F/major', 'backForward': ['G','F'], 'outsideResultNext': 'Cm', 'wrappedPrevious': 'Bm', 'keyboardSelectionAndFocus': ['Bm','Cm','Bm']}


def responsive(page, width, height, label):
    go(page)
    expect(page.locator('[data-practice-chord]')).to_have_count(42)
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), label
    canvas = page.locator(CANVAS)
    assert canvas.evaluate('c=>Boolean(c.getContext("webgl2"))')
    canvas.scroll_into_view_if_needed()
    image = canvas.screenshot()
    pixels = Image.open(BytesIO(image)).convert('RGB')
    pixels.thumbnail((400,400))
    colors = len(pixels.getcolors(pixels.width*pixels.height) or [])
    lit = sum(1 for red,green,blue in pixels.get_flattened_data() if max(red,green,blue)>70 and max(red,green,blue)-min(red,green,blue)>10)
    assert colors > 300 and lit > 250, {'colors':colors,'litColoredPixels':lit}
    shot(page, label + '-canvas', True)
    page.evaluate('document.activeElement?.blur(); window.scrollTo({top:0,behavior:"instant"})')
    shot(page, label + '-page')
    choose(page, 'F')
    diagram(page, 'F')
    page.locator('[data-practice-type="minor7"]').tap() if width <= 1024 else page.locator('[data-practice-type="minor7"]').click()
    expect(page.locator('[data-practice-chord]')).to_have_count(7)
    button = page.locator('[data-practice-chord="Bm7"]')
    button.tap() if width <= 1024 else button.click()
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Bm7')
    diagram(page, 'Bm7')
    assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'), label
    metrics = page.locator('#practice-chord-search, [data-practice-type], [data-practice-previous], [data-practice-next]').evaluate_all('nodes=>nodes.map(e=>{const r=e.getBoundingClientRect();return{element:e.id||e.dataset.practiceType||e.textContent,width:r.width,height:r.height}})')
    assert all(row['width'] > 10 and row['height'] >= 36 for row in metrics), metrics
    shot(page, label + '-filtered')
    return {'viewport': [width,height], 'noOverflow': True, 'filterAndSelectionWorking': True, 'controls': metrics, 'canvasPNGBytes': len(image),'paint':{'colors':colors,'litColoredPixels':lit}}


def touch(page):
    go(page)
    canvas = page.locator(CANVAS)
    canvas.scroll_into_view_if_needed()
    before = json.loads(canvas.get_attribute('data-camera'))
    zoom = page.get_by_role('button', name='ซูมเข้า', exact=True)
    zoom.tap()
    page.wait_for_function('([selector,old])=>JSON.parse(document.querySelector(selector).dataset.camera).distance<old', arg=[CANVAS,before['distance']])
    result = {'nativeTouchZoomButton':True}
    if args.engine == 'chromium':
        canvas.scroll_into_view_if_needed()
        before = json.loads(canvas.get_attribute('data-camera'))
        pixels = Image.open(BytesIO(canvas.screenshot())).convert('RGB')
        box = canvas.bounding_box()
        xx,yy = box['x']+box['width']/2,box['y']+box['height']/2
        session = page.context.new_cdp_session(page)
        def points(distance):
            return [{'id':1,'x':xx-distance,'y':yy,'radiusX':3,'radiusY':3},{'id':2,'x':xx+distance,'y':yy,'radiusX':3,'radiusY':3}]
        session.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':points(30)})
        for distance in [35,40,45,50,55,60]:
            session.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':points(distance)})
        session.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]})
        page.wait_for_function('([selector,old])=>JSON.parse(document.querySelector(selector).dataset.camera).distance<old', arg=[CANVAS,before['distance']])
        page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        after = Image.open(BytesIO(canvas.screenshot())).convert('RGB')
        assert pixels.size == after.size and ImageChops.difference(pixels,after).getbbox(), 'Native pinch must change real rendered pixels'
        session.detach()
        result['nativeCDPTwoFingerPinchChangesCameraAndPixels'] = True
    else:
        result['pinchLimitation'] = 'Linux WebKit has no CDP native multi-touch injection; physical iPad pinch remains untested.'
    return result


def loading(page):
    held = []
    page.route(SCENE, lambda route: held.append(route))
    go(page, ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'loading', timeout=15000)
    expect(page.locator('.practice-scene-state[role="status"]')).to_be_visible()
    choose(page, 'B7', ready=False)
    diagram(page, 'B7')
    assert held, 'Actual independently deferred Three/scene chunk was not held'
    shot(page, 'intentional-scene-loading')
    for route in held: route.continue_()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'B7')
    return {'intentionalFault': 'Hold actual lazy scene/Three module request', 'trainerAvailableDuringLoading': True, 'eventualSelectedChord': 'B7'}


def unsupported(page):
    page.add_init_script('''window.__trainerNativeContext=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(type,...rest){return /^(webgl2?|experimental-webgl)$/.test(type)?null:window.__trainerNativeContext.call(this,type,...rest);};''')
    go(page, ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'error', timeout=30000)
    expect(page.get_by_role('alert')).to_be_visible()
    choose(page, 'F', ready=False)
    diagram(page, 'F')
    shot(page, 'intentional-webgl-unavailable')
    print('PROGRESS',args.engine,'unsupported fallback captured; restoring native WebGL',flush=True)
    # Return a primitive, not the assigned native getContext function: Playwright
    # auto-invokes returned functions, which would call the native method without
    # a canvas receiver and raise an unrelated Illegal invocation.
    page.evaluate('() => { HTMLCanvasElement.prototype.getContext=window.__trainerNativeContext; return true; }')
    print('PROGRESS',args.engine,'native WebGL restored; clicking scene retry',flush=True)
    retry_started = time.monotonic()
    page.locator('[data-practice-retry]').click(timeout=90000)
    print('PROGRESS',args.engine,'scene retry clicked; awaiting ready',flush=True)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'F')
    return {'intentionalFault': 'WebGL context unavailable', 'trainerUsableDuringFault': True,
            'retryPreservesSelection': 'F', 'softwareRendererRecoverySeconds':round(time.monotonic()-retry_started,3)}


def context_loss(page):
    go(page, '/practice?chord=Bm7')
    supported = page.locator(CANVAS).evaluate('''c=>{const extension=c.getContext('webgl2').getExtension('WEBGL_lose_context');if(!extension)return false;extension.loseContext();return true;}''')
    assert supported, 'Context-loss extension not available; cannot call this covered'
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'error')
    diagram(page, 'Bm7')
    shot(page, 'intentional-context-loss')
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'Bm7')
    return {'intentionalFault': 'Actual WEBGL_lose_context extension', 'diagramAvailable': True, 'retryPreservesSelection': 'Bm7'}


def module_failure(page):
    blocked, responses = [], []
    page.on('response', lambda response: responses.append({'url':response.url,'status':response.status}) if SCENE.match(response.url) else None)
    def reject(route):
        blocked.append(route.request.url)
        route.fulfill(status=503, content_type='text/plain', headers={'Cache-Control':'no-store'}, body='Explicit trainer QA scene-module failure')
    page.route(SCENE, reject)
    go(page, ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'error', timeout=30000)
    expect(page.get_by_role('alert')).to_be_visible()
    assert blocked
    choose(page, 'B7', ready=False)
    diagram(page, 'B7')
    page.evaluate('window.__trainerModuleSentinel="same-document"')
    shot(page, 'intentional-module-503')
    page.unroute(SCENE, reject)
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'B7')
    assert page.evaluate('window.__trainerModuleSentinel') == 'same-document'
    assert query(page).get('chord') == ['B7']
    successful = [response for response in responses if response['status'] == 200]
    assert successful and any(response['url'] not in blocked and urlparse(response['url']).query for response in successful), responses
    return {'intentionalFault': 'HTTP503 for actual lazy Three/scene module', 'blockedURLs': blocked, 'responses': responses, 'sameDocumentDistinctURLRetry': True, 'selectedChordPreserved': 'B7'}


def hand_loading(page):
    held = []
    page.route(HAND_MODEL, lambda route: held.append(route))
    go(page, ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status', 'loading')
    assert held, 'The actual anatomical GLB request must be deferred'
    assert hand(page, ready=False)['handVisible'] == 'false'
    choose(page, 'B7')
    diagram(page, 'B7')
    expect(page.locator('[data-practice-hand-review]')).to_have_count(0)
    shot(page, 'intentional-hand-loading')
    for route in held: route.continue_()
    actual = hand(page)
    assert actual['handChordId'] == 'B7' and actual['handVisible'] == 'false'
    return {'intentionalFault':'Hold the actual anatomical GLB request','diagramAndMarkersAvailable':True,'selectedChordPreserved':'B7','actualHand':actual}


def hand_failure(page):
    blocked, requests = [], []
    page.on('request', lambda request: requests.append(request.url) if HAND_MODEL.match(request.url) else None)
    def reject(route):
        blocked.append(route.request.url)
        route.fulfill(status=503, content_type='text/plain', headers={'Cache-Control':'no-store'}, body='Explicit trainer QA anatomical asset failure')
    page.route(HAND_MODEL, reject)
    go(page, ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
    expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status', 'error', timeout=45000)
    assert blocked and hand(page, ready=False)['handVisible'] == 'false'
    choose(page, 'F')
    diagram(page, 'F')
    expect(page.locator('[data-practice-hand-review]')).to_have_count(0)
    expect(page.locator('[data-practice-hand-retry]')).to_be_visible()
    page.evaluate('window.__trainerHandSentinel="same-document"')
    shot(page, 'intentional-hand-503')
    page.unroute(HAND_MODEL, reject)
    page.locator('[data-practice-hand-retry]').click()
    actual = hand(page)
    assert len(requests) >= 2 and actual['handChordId'] == 'F' and actual['handVisible'] == 'false'
    assert page.evaluate('window.__trainerHandSentinel') == 'same-document'
    expect(page.locator('[data-practice-hand-retry]')).to_have_count(0)
    return {'intentionalFault':'HTTP503 for actual anatomical GLB','requests':requests,'selectedChordPreserved':'F','sameDocumentRetry':True,'actualHand':actual}


def prototype_review(page, label):
    go(page)
    initial = hand(page)
    assert initial['handVisible'] == ('true' if 'C' in verified_ids else 'false') and initial['handReviewMode'] == 'false'
    rows = []
    # This is a lifecycle/rendering test. Visible prototype images remain
    # explicitly unapproved and cannot certify anatomy, string contact or fit.
    for chord_id in ['C','F']:
        choose(page, chord_id)
        actual = hand(page)
        if chord_id in verified_ids:
            assert actual['handStatus'] == 'verified' and actual['handVisible'] == 'true' and actual['handReviewMode'] == 'false'
            expect(page.locator('[data-practice-hand-review]')).to_have_count(0)
            expect(page.locator('[data-hand-review-warning]')).to_have_count(0)
            angles = []
            for preset in ['angle','side','back','player']:
                page.locator('[data-camera-preset="'+preset+'"]').click()
                expect(page.locator('[data-camera-preset="'+preset+'"]')).to_have_attribute('aria-pressed','true')
                page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
                shot(page, 'SOURCE-VERIFIED-'+label+'-'+chord_id+'-'+preset, True)
                angles.append({'preset':preset,'camera':json.loads(page.locator(CANVAS).get_attribute('data-camera'))})
            rows.append({'chord':chord_id,'candidateAvailable':True,'sourceIndependentReviewGates':True,
                         'actualHand':actual,'angles':angles,'anatomicalHandApprovalByThisTest':False})
            continue
        if chord_id not in candidate_ids:
            assert actual['handStatus'] == 'unavailable'
            expect(page.locator('[data-practice-hand-review]')).to_have_count(0)
            rows.append({'chord':chord_id,'candidateAvailable':False})
            continue
        expect(page.locator('[data-practice-hand-review]')).to_have_attribute('aria-pressed','false')
        canvas = page.locator(CANVAS)
        canvas.scroll_into_view_if_needed()
        page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        before = Image.open(BytesIO(canvas.screenshot())).convert('RGB')
        page.locator('[data-practice-hand-review]').click()
        expect(page.locator('[data-practice-hand-review]')).to_have_attribute('aria-pressed','true')
        expect(page.locator('[data-hand-review-warning]')).to_be_visible()
        actual = hand(page)
        assert actual['handStatus'] == 'needs-review' and actual['handVisible'] == 'true' and actual['handReviewMode'] == 'true'
        page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        after = Image.open(BytesIO(canvas.screenshot())).convert('RGB')
        assert before.size == after.size
        delta = ImageChops.difference(before,after)
        changed_pixels = sum(1 for px in delta.get_flattened_data() if max(px)>3)
        assert changed_pixels > 100, {'reason':'Prototype visibility must change actual WebGL pixels','changedPixels':changed_pixels}
        angles = []
        for preset in ['angle','side','back','player']:
            page.locator('[data-camera-preset="'+preset+'"]').click()
            expect(page.locator('[data-camera-preset="'+preset+'"]')).to_have_attribute('aria-pressed','true')
            page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
            shot(page, 'UNAPPROVED-prototype-'+label+'-'+chord_id+'-'+preset, True)
            angles.append({'preset':preset,'camera':json.loads(canvas.get_attribute('data-camera'))})
        page.locator('.practice-canvas-stage').screenshot(path=str(args.output/('UNAPPROVED-prototype-'+label+'-'+chord_id+'-warning.png')))
        report['screenshots'].append('UNAPPROVED-prototype-'+label+'-'+chord_id+'-warning.png')
        page.locator('[data-practice-hand-review]').click()
        expect(page.locator('[data-practice-hand-review]')).to_have_attribute('aria-pressed','false')
        expect(page.locator('[data-hand-review-warning]')).to_have_count(0)
        assert hand(page)['handVisible'] == 'false'
        page.locator('[data-camera-preset="angle"]').click()
        rows.append({'chord':chord_id,'candidateAvailable':True,'actualHand':actual,'changedWebGLPixels':changed_pixels,'angles':angles,'anatomicalHandApproval':False})
    return {'viewport':label,'initialHandHidden':initial['handVisible']=='false','explicitReviewAndWarning':any(row.get('changedWebGLPixels',0)>100 for row in rows),'poses':rows,'anatomicalHandApproval':False}


def lazy_routes(page):
    rows = []
    for route in ['/', '/brands', '/guitars']:
        go(page, route, ready=False)
        page.wait_for_load_state('networkidle')
        resources = page.evaluate('performance.getEntriesByType("resource").map(entry=>entry.name)')
        scene = [resource for resource in resources if SCENE.match(resource)]
        hand_resources = [resource for resource in resources if HAND_RESOURCE.match(resource)]
        assert not scene and not hand_resources and page.locator(CANVAS).count() == 0, (route, scene, hand_resources)
        rows.append({'route': route, 'sceneRequests': scene,'handRequests':hand_resources})
    return {'routes': rows}


def spa_cleanup(page):
    go(page)
    choose(page, 'C7')
    page.evaluate('window.__trainerSpaSentinel="same-document"')
    rows = []
    for index in range(2):
        page.locator('.practice-model-note a[href="/guitars"]').click()
        expect(page.locator('#catalog-search')).to_be_visible()
        assert page.locator(CANVAS).count() == 0
        page.go_back(wait_until='domcontentloaded')
        expect(page.locator(STATUS)).to_have_attribute('data-practice-status', 'ready', timeout=45000)
        expect(page.locator(CANVAS)).to_have_attribute('data-chord-id', 'C7')
        assert page.locator(CANVAS).count() == 1
        assert page.evaluate('window.__trainerSpaSentinel') == 'same-document'
        rows.append({'cycle':index+1,'selectedChord':'C7','canvasesAfterBack':1})
    return {'cycles': rows}


def performance_lifecycle(page):
    """Measure actual on-demand frames and bounded repeated SPA allocations.

    JS heap evidence is Chromium-only and excludes native/GPU memory. No
    software-renderer timing here is presented as an iPad frame-rate result.
    """
    go(page)
    hand(page)
    canvas = page.locator(CANVAS)
    expect(canvas).to_have_attribute('data-render-count', re.compile(r'[1-9][0-9]*'))
    page.wait_for_timeout(250)
    first = int(canvas.get_attribute('data-render-count'))
    page.wait_for_timeout(800)
    idle = int(canvas.get_attribute('data-render-count'))
    assert idle == first, 'An idle trainer must not keep rendering WebGL frames'
    info = json.loads(canvas.get_attribute('data-render-info'))
    assert 0 < info['calls'] < 200 and 0 < info['triangles'] < 150000, info
    page.get_by_role('button', name='ซูมเข้า', exact=True).click()
    page.wait_for_function('([selector,count])=>Number(document.querySelector(selector).dataset.renderCount)>count', arg=[CANVAS,idle])
    page.wait_for_timeout(250)
    after_zoom = int(canvas.get_attribute('data-render-count'))
    page.wait_for_timeout(800)
    assert int(canvas.get_attribute('data-render-count')) == after_zoom
    visible_info = None
    review = page.locator('[data-practice-hand-review]')
    if review.count():
        review.click(timeout=90000)
        expect(page.locator('[data-hand-review-warning]')).to_be_visible()
        assert hand(page)['handVisible'] == 'true'
        page.evaluate('new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)))')
        visible_info = json.loads(canvas.get_attribute('data-render-info'))
        assert visible_info['triangles'] > info['triangles'] + 1000, 'The actual skinned human mesh must add real rendered triangles'
        assert visible_info['calls'] < 200 and visible_info['triangles'] < 150000, visible_info
        review.click(timeout=90000)
        assert hand(page)['handVisible'] == 'false'
    elif hand(page)['handVisible'] == 'true':
        visible_info = info
    heap = []
    session = page.context.new_cdp_session(page) if args.engine == 'chromium' else None
    if session:
        session.send('Performance.enable')
    for index in range(3):
        page.locator('.practice-model-note a[href="/guitars"]').click()
        expect(page.locator('#catalog-search')).to_be_visible()
        assert page.locator(CANVAS).count() == 0
        if session:
            session.send('HeapProfiler.collectGarbage')
            values = {row['name']:row['value'] for row in session.send('Performance.getMetrics')['metrics']}
            heap.append({'cycle':index+1,'jsHeapUsedBytesAfterUnmount':int(values['JSHeapUsedSize']),
                         'jsHeapTotalBytes':int(values['JSHeapTotalSize']),'documents':values.get('Documents'),
                         'nodes':values.get('Nodes')})
        page.go_back(wait_until='domcontentloaded')
        expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=45000)
        hand(page)
        assert page.locator(CANVAS).count() == 1
    if session:
        session.detach()
        # Detect a material repeated JS retention regression, allowing expected
        # framework/browser caches. Native driver allocations are not measured.
        assert heap[-1]['jsHeapUsedBytesAfterUnmount'] - heap[0]['jsHeapUsedBytesAfterUnmount'] < 20*1024*1024, heap
    return {'idleRenderCountBefore':first,'idleRenderCountAfter':idle,'zoomRenderCount':after_zoom,
            'renderInfo':info,'visibleHandRenderInfo':visible_info,'spaUnmounts':3,'heap':heap,
            'limitations':['Software WebGL engine measurements are not physical iPad GPU/frame-rate evidence.',
                           'JS heap measurements do not measure native WebGL/GPU memory.']}


def context_for(browser, name, width, height, fault):
    context = browser.new_context(viewport={'width':width,'height':height}, has_touch=width<=1024, locale='th-TH', reduced_motion='reduce')
    page = context.new_page()
    def expected_fault(text='', url=''):
        return (fault == 'module' and (SCENE.match(url) or bool(re.search(r'503|module script|dynamically imported module|mime type|loading module',text,re.I)))) or (fault == 'hand' and (HAND_RESOURCE.match(url) or bool(re.search(r'503',text)))) or bool(fault is True and re.search(r'webgl|context.?lost|context creation', text, re.I))
    def console(message):
        if message.type == 'warning': report['warnings'].append({'case':name,'text':message.text})
        if message.type != 'error': return
        row = {'case':name,'text':message.text,'location':message.location}
        report['expectedFaultErrors' if expected_fault(message.text, message.location.get('url','')) else 'consoleErrors'].append(row)
    page.on('console', console)
    page.on('pageerror', lambda error: report['runtimeErrors'].append({'case':name,'text':str(error)}))
    page.on('requestfailed', lambda request: report['expectedFaultErrors' if expected_fault('',request.url) else 'failedRequests'].append({'case':name,'url':request.url,'failure':request.failure}))
    page.on('response', lambda response: report['expectedFaultErrors' if expected_fault('',response.url) else 'badResponses'].append({'case':name,'url':response.url,'status':response.status}) if response.status >= 400 else None)
    return context, page


cases = [('all-42-diagrams',all_chords,1440,1000,False), ('search-filters',filters,1440,1000,False),
         ('navigation-history-keyboard',navigation_history,1440,1000,False)]
cases += [('responsive-'+label,lambda page,w=w,h=h,label=label:responsive(page,w,h,label),w,h,False)
          for w,h,label in [(1440,1000,'desktop'),(1024,768,'tablet-landscape'),(768,1024,'tablet'),(390,844,'mobile'),(320,740,'small-mobile')]]
cases += [('loading',loading,768,1024,False),('webgl-unavailable',unsupported,390,844,True),('context-loss',context_loss,768,1024,True),
          ('module-failure',module_failure,768,1024,'module'),('touch',touch,768,1024,False),('lazy-routes',lazy_routes,1440,1000,False),('spa-cleanup',spa_cleanup,1440,1000,False)]
cases += [('hand-loading',hand_loading,768,1024,False),('hand-failure',hand_failure,768,1024,'hand')]
cases += [('performance-lifecycle',performance_lifecycle,1440,1000,False)]
cases += [('hand-review-'+label,lambda page,label=label:prototype_review(page,label),w,h,False)
          for w,h,label in [(1440,1000,'desktop'),(768,1024,'tablet'),(390,844,'mobile')]]
selected = [case for case in args.cases.split(',') if case]
try:
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']) if args.engine == 'chromium' else playwright.webkit.launch()
        report['browserVersion'] = browser.version
        for name, function, width, height, fault in cases:
            if selected and not any(name.startswith(prefix) for prefix in selected): continue
            context, page = context_for(browser,name,width,height,fault)
            try:
                details = function(page)
                report['checks'].append({'case':name,'passed':True,'details':details})
                print('PASS',args.engine,name,flush=True)
            except Exception:
                failure = traceback.format_exc()
                report['checks'].append({'case':name,'passed':False,'failure':failure,'url':page.url})
                try: shot(page,'failure-'+name)
                except Exception: pass
                print('FAIL',args.engine,name,failure,flush=True)
            finally:
                context.close()
        browser.close()
except Exception:
    report['harnessFailure'] = traceback.format_exc()
    print(report['harnessFailure'],flush=True)
finally:
    report['productionArtifactSHA256'] = build_before
    report['buildArtifactsUnchangedDuringRun'] = build_before == build_snapshot()
    report['passed'] = bool(report['checks']) and all(check['passed'] for check in report['checks']) and not report.get('harnessFailure') and not any(report[key] for key in ['consoleErrors','runtimeErrors','failedRequests','badResponses']) and report['buildArtifactsUnchangedDuringRun']
    suffix = '-' + '-'.join(selected) if selected else ''
    (args.output / ('browser-trainer-' + args.engine + suffix + '.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2) + '\n')
raise SystemExit(0 if report['passed'] else 1)
