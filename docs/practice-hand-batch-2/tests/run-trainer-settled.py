"""Run the unchanged trainer assertions with explicit startup idle readiness.

The initial Chromium run exposed one queued hand-publish rAF after asset-ready.
Wait for that pending work and bounded stable dimensions/count before measuring
idle. The original 800ms no-render assertion and all other cases stay unchanged.
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

output_index = sys.argv.index('--output') + 1
output = Path(sys.argv[output_index])
output.mkdir(parents=True, exist_ok=True)
manifest = {'originalSuite':str(original.relative_to(ROOT)),
            'originalSuiteSHA256':hashlib.sha256(original.read_bytes()).hexdigest(),
            'adaptedSuiteSHA256':hashlib.sha256(source.encode()).hexdigest(),
            'adaptation':'Only performance startup readiness: two existing animation frames then bounded300msstableframe-count/dimensions; original250msbeforefirstsampleand800msidleassertremainunchanged.',
            'appSourceModified':False,'originalSuiteModified':False,
            'reasonEvidence':'../idle-startup-timeline.json'}
(output / 'harness-adaptation.json').write_text(json.dumps(manifest,indent=2)+'\n')
exec(compile(source,str(original),'exec'),{'__name__':'__main__','__file__':str(original)})
