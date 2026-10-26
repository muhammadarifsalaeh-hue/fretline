"""Run the existing 21-case plan with explicit startup and stricter bad-pose rejection.

The initial Chromium run exposed one queued hand-publish rAF after asset-ready.
Wait for that pending work and bounded stable dimensions/count before measuring
idle. The original 800ms no-render assertion stays unchanged. The rejected-F
inspection branch below is separately strengthened to require diagram fallback.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
original = ROOT / 'docs/practice-trainer/tests/browser-trainer.py'
source = original.read_text()
marker = "    expect(canvas).to_have_attribute('data-render-count', re.compile(r'[1-9][0-9]*'))\n    page.wait_for_timeout(250)"
assert source.count(marker) == 1, 'Idle readiness adaptation must have exactly one known location'
helper = '''
def wait_for_initial_canvas_settlement(page, canvas):
    # Asset-ready is published before its invalidated frame. Await existing
    # queued rAF work, then require 300ms stable frame count and actual size.
    page.evaluate('new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)))')
    start=time.monotonic(); stable_since=None; previous=None; samples=[]
    while time.monotonic()-start < 10:
        state=canvas.evaluate('c=>({count:Number(c.dataset.renderCount),width:c.getBoundingClientRect().width,height:c.getBoundingClientRect().height,asset:c.dataset.handAssetStatus})')
        samples.append({'elapsedSeconds':time.monotonic()-start,**state})
        if state==previous and state['asset']=='ready' and state['width']>0 and state['height']>0:
            if stable_since is None:stable_since=time.monotonic()
            if time.monotonic()-stable_since>=.3:return samples
        else:stable_since=None
        previous=state
        page.wait_for_timeout(100)
    raise AssertionError(('Startup canvas did not settle within10seconds',samples))

'''
source = source.replace('def performance_lifecycle(page):', helper + 'def performance_lifecycle(page):', 1)
source = source.replace(marker, marker.replace('    page.wait_for_timeout(250)', '    startup_settlement = wait_for_initial_canvas_settlement(page, canvas)\n    page.wait_for_timeout(250)'), 1)
return_marker = "    return {'idleRenderCountBefore':first,'idleRenderCountAfter':idle,"
assert source.count(return_marker) == 1
source = source.replace(return_marker, "    return {'startupSettlement':startup_settlement,'idleRenderCountBefore':first,'idleRenderCountAfter':idle,", 1)
assert "assert idle == first, 'An idle trainer must not keep rendering WebGL frames'" in source
assert "page.wait_for_timeout(800)" in source

# The final delivery closes inspection of a known rejected pose. Preserve the
# C allowed-prototype pixel/4-camera assertions; strengthen the F path instead
# of expecting the old unsafe F inspection button. All42 source poses still
# receive their actual hidden bone/root fingerprints in the canonical loop.
inspection_marker="candidate_ids = {key for key, record in pose_library.get('poses', {}).items() if record.get('status') != 'unavailable'}"
assert source.count(inspection_marker)==1
source=source.replace(inspection_marker,inspection_marker+"\ninspection_ids = {key for key,record in pose_library.get('poses',{}).items() if record.get('audit',{}).get('collisionPassed') is True and record.get('audit',{}).get('contactPassed') is True and record.get('status') in ['needs-review','verified']}",1)
fields_marker="'handChordId','handReviewMode','handPoseSignature','handModelSha256']"
assert source.count(fields_marker)==1
source=source.replace(fields_marker,"'handChordId','handReviewMode','handPoseSignature','handModelSha256','handInspectionAllowed']",1)
ready_marker="    if value['handAssetStatus'] == 'ready':\n"
assert source.count(ready_marker)==1
source=source.replace(ready_marker,ready_marker+"        assert value['handInspectionAllowed'] == ('true' if value['handChordId'] in inspection_ids else 'false'), value\n        if value['handInspectionAllowed'] == 'false':\n            assert value['handVisible'] == 'false' and value['handReviewMode'] == 'false', 'Rejected geometry cannot become a visible inspection example'\n",1)
review_marker="        expect(page.locator('[data-practice-hand-review]')).to_have_attribute('aria-pressed','false')\n        canvas = page.locator(CANVAS)\n"
assert source.count(review_marker)==1
blocked='''        if chord_id not in inspection_ids:
            assert actual['handStatus'] == 'needs-review'
            assert actual['handVisible'] == 'false' and actual['handReviewMode'] == 'false'
            assert actual['handInspectionAllowed'] == 'false'
            expect(page.locator('[data-practice-hand-review]')).to_have_count(0)
            expect(page.locator('[data-hand-review-warning]')).to_have_count(0)
            checked_diagram = diagram(page, chord_id)
            canvas = page.locator(CANVAS)
            assert canvas.get_attribute('data-string-pose') == 'open'
            rendered = Image.open(BytesIO(canvas.screenshot())).convert('RGB')
            assert len(rendered.getcolors(rendered.width*rendered.height) or []) > 300
            shot(page, 'REJECTED-hand-diagram-fallback-'+label+'-'+chord_id, True)
            rows.append({'chord':chord_id,'candidateAvailable':True,'inspectionAllowed':False,
                         'rejectedHandHidden':True,'actualHand':actual,'checkedDiagram':checked_diagram,
                         'openStringFallback':True,'nonemptyActualWebGLCanvas':True,
                         'anatomicalHandApproval':False})
            continue
'''
source=source.replace(review_marker,blocked+review_marker,1)

output_index = sys.argv.index('--output') + 1
output = Path(sys.argv[output_index])
output.mkdir(parents=True, exist_ok=True)
manifest = {'originalSuite':str(original.relative_to(ROOT)),
            'originalSuiteSHA256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'adaptedSuiteSHA256':hashlib.sha256(source.encode()).hexdigest(),
            'adaptation':'Performance startup readiness: two existing animation frames then bounded300msstableframe-count/dimensions; original250msbeforefirstsampleand800msidleassertremainunchanged. The independent stricter inspection policy adaptation is recorded below.',
            'appSourceModified':False,'originalSuiteModified':False,
            'finalPolicyAdaptation':'All42 actual hidden bone fingerprints retained; geometry-rejected F cannot expose inspection. C allowed hand retains actual pixel and four-camera assertions. Rejected F now requires absent review control, hidden hand, actual correct SVG diagram, open-string fallback and a drawn WebGL canvas.',
            'reasonEvidence':'../../../practice-hand-batch-2/tests/reports/idle-startup-timeline.json'}
(output / 'harness-adaptation.json').write_text(json.dumps(manifest,indent=2)+'\n')
exec(compile(source,str(original),'exec'),{'__name__':'__main__','__file__':str(original)})
