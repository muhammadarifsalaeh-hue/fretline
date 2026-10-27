"""Focused Practice UI probes, preserving the original independent SVG criteria.

No import-time browser launch, app edit, build or hand-pose approval. Parent QA
calls these functions on its frozen production build and owns aggregate errors.
All 42 diagrams are checked against the preexisting independent voicing fixture;
original finger/note assignments are separately bound to baseline 985d0c4.
"""
from pathlib import Path
from io import BytesIO
from urllib.parse import parse_qs, urlparse
import hashlib, json, re
from PIL import Image, ImageChops
from playwright.sync_api import expect

ROOT=Path(__file__).resolve().parents[3]
CANVAS='canvas[data-practice-canvas]'
STATUS='[data-practice-status]'
original=json.loads((Path(__file__).parent/'practice-fixture.json').read_text())
fixture=json.loads((ROOT/'docs/practice-trainer/tests/reference-voicings.json').read_text())
assert hashlib.sha256((ROOT/'src/features/practice/data/chords.js').read_bytes()).hexdigest()==original['sourceSHA256'], 'Chord data changed from protected baseline'
assert hashlib.sha256((ROOT/'docs/practice-trainer/tests/reference-voicings.json').read_bytes()).hexdigest()==original['referenceVoicingsSHA256'], 'Independent voicing fixture changed'
expected={key:{'frets':[None if f=='x' else int(f) for f in shape],'type':group['type']} for group in fixture['groups'] for key,shape in group['voicings'].items()}
data={entry['id']:entry for entry in original['chords']}
assert len(expected)==len(data)==42 and list(expected)==list(data)

def query(page):return parse_qs(urlparse(page.url).query)
def settle(page):page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
def go(page,base,ready=True):
    page.goto(base.rstrip('/')+'/practice?chord=C',wait_until='networkidle')
    page.evaluate('document.fonts.ready')
    if ready:
        expect(page.locator(STATUS)).to_have_attribute('data-practice-status','ready',timeout=45000)
        expect(page.locator(CANVAS)).to_be_visible()
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','ready',timeout=60000)

def availability(page,base):
    go(page,base,ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status',re.compile('^(ready|error)$'),timeout=60000)
    actual=page.locator(STATUS).get_attribute('data-practice-status')
    native=page.evaluate("""()=>{const c=document.createElement('canvas'),gl=c.getContext('webgl2',{alpha:true,antialias:true,powerPreference:'low-power'});const available=!!gl;if(gl)gl.getExtension('WEBGL_lose_context')?.loseContext();return available;}""")
    if actual=='ready':
        assert native,'Ready scene must have native WebGL2 support'
        expect(page.locator(CANVAS)).to_be_visible()
        expect(page.locator(CANVAS)).to_have_attribute('data-hand-asset-status','ready',timeout=60000)
        return True
    assert not native,'Scene failed although native WebGL2 is available; do not treat an app error as unsupported graphics'
    expect(page.get_by_role('alert')).to_be_visible()
    assert page.locator(CANVAS).count()==0
    return False

def choose(page,chord_id,ready=True):
    button=page.locator('[data-practice-chord="'+chord_id+'"]')
    button.click()
    expect(button).to_have_attribute('aria-pressed','true')
    expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord',chord_id)
    if ready:expect(page.locator(CANVAS)).to_have_attribute('data-chord-id',chord_id)
    assert query(page).get('chord')==[chord_id]

def state(page):
    return page.locator(CANVAS).evaluate("""c=>({chord:c.dataset.chordId,renderCount:Number(c.dataset.renderCount),
      handChord:c.dataset.handChordId,handStatus:c.dataset.handStatus,handVisible:c.dataset.handVisible,
      handReview:c.dataset.handReviewMode,handAsset:c.dataset.handAssetStatus,stringPose:c.dataset.stringPose,
      camera:JSON.parse(c.dataset.camera),projection:JSON.parse(c.dataset.practiceProjection),
      strings:Number(c.dataset.stringCount),frets:Number(c.dataset.fretCount),info:JSON.parse(c.dataset.renderInfo)})""")

def hand_is_safe(actual,chord_id):
    assert actual['chord']==actual['handChord']==chord_id,actual
    assert actual['handStatus'] in ['verified','needs-review','unavailable']
    # UI refinement cannot promote an unreviewed anatomical hand to a lesson.
    assert actual['handStatus']!='verified',actual
    assert actual['handVisible']=='false' and actual['handReview']=='false',actual
    assert actual['stringPose']=='open',actual
    assert actual['strings']==6 and actual['frets']==12
    assert actual['renderCount']>0 and actual['info']['calls']>0 and actual['info']['triangles']>0

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

def practice_all_chords(page,base,engine,output=None):
    ready=availability(page,base)
    expect(page.locator('[data-practice-chord]')).to_have_count(42)
    assert page.locator('[data-practice-chord]').evaluate_all('n=>n.map(x=>x.dataset.practiceChord)')==list(expected)
    page.evaluate('window.__samePracticeDocument="preserved"')
    rows=[]
    for chord_id in expected:
        compact=diagram(page,chord_id,compact=True)
        choose(page,chord_id,ready=ready)
        full=diagram(page,chord_id)
        detail=page.locator('[data-practice-active-chord]')
        fretted=[(6-i,f,data[chord_id]['fingers'][i]) for i,f in enumerate(expected[chord_id]['frets']) if f is not None and f>0]
        instructions=detail.locator('[data-finger-instruction]')
        assert instructions.count()==len(fretted)
        rendered=[]
        for item in instructions.all():
            position=(int(item.get_attribute('data-string')),int(item.get_attribute('data-fret')),int(item.get_attribute('data-finger-instruction')))
            assert position in fretted,(chord_id,position,fretted)
            text=item.inner_text();string,fret,finger=position
            assert str(string) in text and str(fret) in text and data[chord_id]['notes'][6-string] in text
            rendered.append(position)
        assert sorted(rendered)==sorted(fretted)
        assert detail.locator('[data-barre-instruction]').count()==len(data[chord_id]['barres'])
        for index,barre in enumerate(data[chord_id]['barres']):
            text=detail.locator('[data-barre-instruction]').nth(index).inner_text()
            assert all(str(barre[key]) in text for key in ['fret','fromString','toString'])
        status=detail.locator('.practice-string-status dd').all_text_contents()
        assert len(status)==2
        for text,value in zip(status,[0,None]):
            assert [int(n) for n in re.findall(r'\d+',text)]==[6-i for i,f in enumerate(expected[chord_id]['frets']) if f==value]
        assert page.evaluate('window.__samePracticeDocument')=='preserved'
        actual=state(page) if ready else None
        if ready:
            hand_is_safe(actual,chord_id)
            assert page.locator(CANVAS).count()==1
        else:
            assert page.locator(CANVAS).count()==0
            expect(page.get_by_role('alert')).to_be_visible()
        rows.append({'id':chord_id,'fullDiagram':full,'compactDiagram':compact,'fingerInstructions':rendered,
          'renderedChordId':actual['chord'] if ready else None,'handStatus':actual['handStatus'] if ready else 'native-webgl2-unavailable','handHidden':True,
          'realWebGLDrawCalls':actual['info']['calls'] if ready else 0,'realWebGLTriangles':actual['info']['triangles'] if ready else 0})
        if len(rows)%7==0:print('PROGRESS',engine,'Practice diagrams/strings/instructions',len(rows),'/42',flush=True)
    if output:
        Path(output).mkdir(parents=True,exist_ok=True)
        (Path(output)/f'{engine}-practice-42.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2)+'\n')
    return {'checked':42,'fullAndCompactDiagrams':84,'actualCanvasUpdates':42 if ready else 0,'nativeWebGL2Available':ready,'threeDTested':ready,'fallbackUsableForAll42':not ready,'unchangedDocument':True,
      'handApprovals':0,'unapprovedHandsHidden':42,'chords':rows,
      'markerLimit':'Canvas changes and the unchanged source-bound marker calculations are checked; this is not anatomical fingertip approval.'}

def practice_filters_navigation(page,base,engine):
    ready=availability(page,base)
    def selected(chord_id):
        expect(page.locator('[data-practice-active-chord]')).to_have_attribute('data-practice-active-chord',chord_id)
        if ready:expect(page.locator(CANVAS)).to_have_attribute('data-chord-id',chord_id)
    rows=[]
    for kind in original['types']:
        page.locator('[data-practice-type="'+kind['id']+'"]').click()
        wanted=[key for key,item in expected.items() if item['type']==kind['id']]
        actual=page.locator('[data-practice-chord]').evaluate_all('n=>n.map(x=>x.dataset.practiceChord)')
        assert actual==wanted,(kind,actual,wanted)
        expect(page.locator('[data-practice-result-count]')).to_have_attribute('data-practice-result-count',str(len(wanted)))
        assert query(page).get('type')==[kind['id']]
        rows.append({'type':kind['id'],'models':wanted})
    page.locator('[data-practice-type="all"]').click()
    search=page.locator('#practice-chord-search')
    for text,types in [('C',None),('Am',None),('dominant 7',None),('ZZZ-nothing',None)]:
        search.fill(text)
        if text=='C':wanted=[key for key,item in data.items() if item['root']=='C']
        elif text=='Am':wanted=[key for key,item in data.items() if 'am' in key.lower() or 'am' in item['fullName'].lower() or 'am' in item['quality'].lower() or 'am' in item['type'].lower() or 'am' in item['voicing'].lower()]
        elif text=='dominant 7':wanted=[key for key,item in data.items() if item['type']=='dominant7']
        else:wanted=[]
        expect(page.locator('[data-practice-result-count]')).to_have_attribute('data-practice-result-count',str(len(wanted)))
        assert page.locator('[data-practice-chord]').evaluate_all('n=>n.map(x=>x.dataset.practiceChord)')==wanted
        if not wanted:
            expect(page.locator('.practice-chord-empty')).to_be_visible()
        rows.append({'query':text,'ids':wanted})
    search.fill('');page.locator('[data-practice-type="major"]').click();choose(page,'C',ready=ready)
    expect(page.locator('.practice-navigation-count')).to_contain_text('1 / 7')
    page.locator('[data-practice-next]').click();selected('D')
    expect(page.locator('.practice-navigation-count')).to_contain_text('2 / 7')
    page.locator('[data-practice-previous]').click();selected('C')
    page.locator('[data-practice-previous]').click();selected('B')
    expect(page.locator('.practice-navigation-count')).to_contain_text('7 / 7')
    page.locator('[data-practice-chord="B"]').focus();page.keyboard.press('Home')
    selected('C')
    page.keyboard.press('ArrowRight');selected('D')
    page.keyboard.press('End');selected('B')
    page.locator('[data-practice-type="all"]').click();choose(page,'C',ready=ready)
    expect(page.locator('.practice-navigation-count')).to_contain_text('1 / 42')
    if ready:expect(page.locator(CANVAS)).to_have_attribute('data-chord-id','C')
    return {'nativeWebGL2Available':ready,'threeDTested':ready,'types':rows,'allSixTypes':True,'queryEmptyState':True,'filteredPreviousNextWrap':True,
      'keyboardHomeEndArrows':True,'unfilteredCounter':'1 / 42'}

def camera_state(page):return state(page)['camera']
def same_camera(a,b):
    return all(abs(x-y)<2e-5 for key in ['position','target','up'] for x,y in zip(a[key],b[key])) and abs(a['distance']-b['distance'])<2e-5

def real_pixels(page):
    settle(page);return Image.open(BytesIO(page.locator(CANVAS).screenshot(timeout=60000))).convert('RGB')
def changed_pixels(a,b):
    assert a.size==b.size,(a.size,b.size)
    count=sum(max(px)>3 for px in ImageChops.difference(a,b).get_flattened_data())
    assert count>100,('A real camera control must change drawn pixels',count)
    return count

def practice_camera(page,base,engine,output=None):
    ready=availability(page,base)
    if not ready:
        return {'notTested':True,'threeDTested':False,'nativeWebGL2Available':False,'reason':'Native WebGL2 unavailable in this engine; actual 3D camera controls could not be verified. Visible fallback and all 42 diagrams tested separately.','physicalIPadTested':False}
    canvas=page.locator(CANVAS);canvas.scroll_into_view_if_needed()
    initial=state(page);head,body=initial['projection']['headstock'],initial['projection']['body']
    assert head[0]>body[0] and head[1]>body[1]
    strings=initial['projection']['strings']
    assert [s['number'] for s in strings]==[6,5,4,3,2,1]
    assert [s['note'] for s in strings]==['E2','A2','D3','G3','B3','E4']
    assert all(strings[i]['radius']>strings[i+1]['radius'] for i in range(5))
    assert all(strings[i]['ndc'][1]>strings[i+1]['ndc'][1] for i in range(5))
    previous=initial;image=real_pixels(page);rows=[]
    presets=page.locator('[data-camera-preset]')
    for preset in presets.evaluate_all('nodes=>nodes.map(n=>n.dataset.cameraPreset)'):
        # Current angle can legitimately be the active initial camera.
        if preset=='angle':continue
        button=page.locator('[data-camera-preset="'+preset+'"]')
        if not button.is_visible():
            for details in page.locator('details').all():
                if details.locator('[data-camera-preset="'+preset+'"]').count():details.locator('summary').click()
        button.click();expect(button).to_have_attribute('aria-pressed','true')
        current=state(page);new_image=real_pixels(page)
        assert not same_camera(previous['camera'],current['camera'])
        assert current['projection']['geometrySignature']==initial['projection']['geometrySignature']
        hand_is_safe(current,'C')
        rows.append({'preset':preset,'changedPixels':changed_pixels(image,new_image),'camera':current['camera']})
        previous,image=current,new_image
    page.get_by_role('button',name='รีเซ็ตกล้อง',exact=True).click();reset=state(page);image=real_pixels(page)
    assert same_camera(initial['camera'],reset['camera'])
    controls=[]
    for label,kind in [('หมุนไปทางซ้าย','rotate'),('หมุนไปทางขวา','rotate'),('ซูมเข้า','in'),('ซูมออก','out')]:
        previous=state(page);old_image=real_pixels(page)
        page.get_by_role('button',name=label,exact=True).click()
        current=state(page);new_image=real_pixels(page)
        assert not same_camera(previous['camera'],current['camera'])
        assert current['projection']['geometrySignature']==initial['projection']['geometrySignature']
        if kind=='in':assert current['camera']['distance']<previous['camera']['distance']
        if kind=='out':assert current['camera']['distance']>previous['camera']['distance']
        controls.append({'button':label,'changedPixels':changed_pixels(old_image,new_image)})
    page.get_by_role('button',name='รีเซ็ตกล้อง',exact=True).click();settle(page)
    assert same_camera(initial['camera'],camera_state(page))
    canvas.focus();page.keyboard.press('ArrowLeft');assert not same_camera(initial['camera'],camera_state(page))
    page.keyboard.press('0');assert same_camera(initial['camera'],camera_state(page))
    if output:
        Path(output).mkdir(parents=True,exist_ok=True);canvas.screenshot(path=str(Path(output)/f'{engine}-practice-reset.png'),timeout=60000)
    return {'threeDTested':True,'nativeWebGL2Available':True,'defaultLowEAboveHighE':True,'headstockUpperRight':True,'presets':rows,'buttons':controls,
      'keyboardAndButtonReset':True,'geometryUnchangedByCamera':True,'physicalIPadTested':False}

def practice_webgl_fallback(page,base,engine,output=None):
    page.add_init_script("""window.__practiceOriginalContext=HTMLCanvasElement.prototype.getContext;
      HTMLCanvasElement.prototype.getContext=function(type,...rest){return /^(webgl2?|experimental-webgl)$/.test(type)?null:window.__practiceOriginalContext.call(this,type,...rest);};""")
    go(page,base,ready=False)
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status','error',timeout=45000)
    expect(page.get_by_role('alert')).to_be_visible()
    error=page.get_by_role('alert').inner_text()
    assert len(error)<350,('Fallback message must remain concise',len(error))
    choose(page,'F',ready=False);diagram(page,'F')
    expect(page.locator('[data-practice-chord]')).to_have_count(42)
    expect(page.locator('[data-practice-active-chord]')).to_contain_text('F Major')
    assert page.locator(CANVAS).count()==0
    if output:
        Path(output).mkdir(parents=True,exist_ok=True);page.screenshot(path=str(Path(output)/f'{engine}-practice-webgl-fallback.png'),full_page=True,timeout=60000)
    page.evaluate('()=>{HTMLCanvasElement.prototype.getContext=window.__practiceOriginalContext;return true}')
    page.locator('[data-practice-retry]').click()
    expect(page.locator(STATUS)).to_have_attribute('data-practice-status',re.compile('^(ready|error)$'),timeout=60000)
    recovered=page.locator(STATUS).get_attribute('data-practice-status')=='ready'
    if recovered:expect(page.locator(CANVAS)).to_have_attribute('data-chord-id','F')
    else:
        native=page.evaluate("()=>!!document.createElement('canvas').getContext('webgl2')");assert not native,'Retry failed despite restored native WebGL2'
        expect(page.get_by_role('alert')).to_be_visible();diagram(page,'F');assert page.locator(CANVAS).count()==0
    return {'intentionalWebGLUnavailable':True,'nativeWebGL2AvailableAfterRestore':recovered,'realRetryTo3D':recovered,'visibleBriefAlert':error,'FBarreDiagramUsable':True,
      'all42ChoicesRetained':True,'realRetryPreservedSelection':'F','selectionPreservedWithFallbackIfNativeUnavailable':not recovered,'physicalIPadTested':False}
