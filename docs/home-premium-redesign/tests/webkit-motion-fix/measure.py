"""Replay frame-bound timing measurements; run with the configured WebKit runtime."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import argparse, json

parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:5454')
parser.add_argument('--output', type=Path, default=Path(__file__).with_name('replay.json'))
args = parser.parse_args()
sample = '''e=>new Promise(resolve=>requestAnimationFrame(t=>resolve({
    t, now:performance.now(), x:e.scrollLeft, mode:e.dataset.marqueeMotion
})))'''
records = []
with sync_playwright() as p:
    browser = p.webkit.launch()
    for name, width, height in [('desktop',1440,1000), ('tablet',768,1024), ('mobile',390,844)]:
        context = browser.new_context(viewport={'width':width, 'height':height}, reduced_motion='no-preference', has_touch=width<1024)
        page = context.new_page()
        page.goto(args.url, wait_until='networkidle')
        rail = page.locator('[data-marquee-viewport]')
        rail.evaluate('(e)=>e.scrollIntoView({block:"center"})')
        page.wait_for_timeout(200)
        before = rail.evaluate(sample)
        page.wait_for_timeout(800)
        after = rail.evaluate(sample)
        span = after['t']-before['t']
        distance = after['x']-before['x']
        width_px = rail.locator('[data-marquee-primary]').evaluate('(e)=>e.getBoundingClientRect().width')
        distance %= width_px
        rate = 1000*distance/span
        records.append({'viewport':name,'before':before,'after':after,'actualAnimationSpanMs':span,'distance':distance,'pixelsPerSecond':rate})
        assert 27 <= rate <= 33, records[-1]
        context.close()
    browser.close()
args.output.write_text(json.dumps(records, indent=2)+'\n')
print('PASS three actual WebKit animation-bound speed measurements')
