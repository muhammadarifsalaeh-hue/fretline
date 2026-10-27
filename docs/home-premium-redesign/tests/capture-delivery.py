"""Actual viewport screenshots, preserving navigation and default UI behavior.

Long element screenshots may stitch fixed-position items into the content;
these viewport captures complement the full-page QA evidence.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'docs/home-premium-redesign/screenshots'
OUT.mkdir(exist_ok=True)
report = {'physicalIPadSafariTested': False, 'screenshots': [], 'errors': [], 'measurements': []}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for label, width, height in [('desktop', 1440, 1100), ('tablet', 768, 1024), ('mobile', 390, 844)]:
        context = browser.new_context(viewport={'width': width, 'height': height}, reduced_motion='reduce', has_touch=width < 1024)
        context.add_init_script("""window.__shifts=[];new PerformanceObserver(list=>{
          for(const e of list.getEntries())if(!e.hadRecentInput)__shifts.push(e.value);
        }).observe({type:'layout-shift',buffered:true});""")
        page = context.new_page()
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        page.on('console', lambda m: report['errors'].append(m.text) if m.type == 'error' else None)
        page.goto('http://127.0.0.1:5451/', wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        regions = [
            ('hero', '#top'), ('brands', '#brands'), ('categories', '#categories'),
            ('quiz', '#find'), ('quiz-panel', '[data-home-quiz-panel]'),
            ('compare', '#compare'), ('compare-panel', '.home-compare-preview'),
        ]
        for name, selector in regions:
            region = page.locator(selector)
            for im in region.locator('img').all():
                if im.is_visible():
                    im.scroll_into_view_if_needed()
                    im.evaluate('(i)=>i.decode()')
            region.evaluate("""el=>{const header=document.querySelector('.site-header').getBoundingClientRect().height;
              window.scrollBy(0,el.getBoundingClientRect().top-header-14)}""")
            if name == 'hero':
                page.evaluate('scrollTo(0,0)')
            page.screenshot(path=str(OUT / f'{label}-{name}.png'), animations='disabled')
            report['screenshots'].append(f'{label}-{name}.png')
        observation = page.evaluate("""()=>({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,
          cls:__shifts.reduce((a,b)=>a+b,0),resources:performance.getEntriesByType('resource').map(r=>({path:new URL(r.name).pathname,bytes:r.encodedBodySize,durationMs:r.duration}))})""")
        assert observation['scrollWidth'] <= width + 1
        assert not any('practice-three' in r['path'] or r['path'].endswith('.glb') for r in observation['resources'])
        report['measurements'].append({'viewport': label, **observation})
        context.close()
    browser.close()

report['passed'] = len(report['screenshots']) == 21 and not report['errors']
(OUT / 'capture-results.json').write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
print('Viewport delivery:', report['passed'], len(report['screenshots']), 'actual screenshots')
assert report['passed'], report
