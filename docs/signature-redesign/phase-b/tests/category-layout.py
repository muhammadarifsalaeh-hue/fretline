"""Check category alignment and intact Thai words after the typography changes."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, os

OUT = Path(__file__).resolve().parents[1]
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5201')
report = {'checks': [], 'consoleErrors': [], 'runtimeErrors': []}
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for width, height in [(1440,1000),(1024,768),(768,1024),(390,844),(320,740)]:
        context = browser.new_context(viewport={'width':width,'height':height}, reduced_motion='reduce', has_touch=width<=1024)
        page = context.new_page()
        page.on('pageerror', lambda e: report['runtimeErrors'].append(str(e)))
        page.on('console', lambda m: report['consoleErrors'].append(m.text) if m.type=='error' else None)
        page.goto(BASE+'/guitars', wait_until='networkidle')
        expect(page.locator('.catalog-grid article')).to_have_count(9)
        metrics = page.locator('.category-navigation-item').evaluate_all('''buttons => buttons.map(button => {
          const r=button.getBoundingClientRect(),icon=button.querySelector('svg').getBoundingClientRect();
          return {name:button.textContent.trim(),width:r.width,height:r.height,iconCenterY:icon.top+icon.height/2,
            words:[...button.querySelectorAll('.category-navigation-label > span')].map(word=>({
              text:word.textContent,height:word.getBoundingClientRect().height,lineHeight:parseFloat(getComputedStyle(word).lineHeight),
              left:word.getBoundingClientRect().left,right:word.getBoundingClientRect().right}))};
        })''')
        assert len(metrics)==5
        assert max(m['iconCenterY'] for m in metrics)-min(m['iconCenterY'] for m in metrics)<=1, metrics
        for item in metrics:
            assert item['height']>=44 and item['width']>=44, item
            for word in item['words']:
                assert word['height']<=word['lineHeight']+1, word
                assert word['left']>=0 and word['right']<=width, word
        assert page.evaluate('document.documentElement.scrollWidth <= innerWidth+1')
        page.locator('.category-navigation-item').nth(1).click()
        expect(page).to_have_url(BASE+'/guitars?type=electric')
        expect(page.locator('.catalog-grid article')).to_have_count(9)
        page.go_back(wait_until='networkidle')
        expect(page.locator('.category-navigation-item').first).to_have_attribute('aria-pressed','true')
        report['checks'].append({'width':width,'passed':True,'buttons':metrics})
        print(f'PASS category layout / Thai words / filter history at {width}px',flush=True)
        context.close()
    browser.close()
report['passed']=len(report['checks'])==5 and not report['consoleErrors'] and not report['runtimeErrors']
(OUT/'category-layout.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
