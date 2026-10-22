"""Smoke-check shared pages and capture long mobile review frames at 390px."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, math, traceback

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT/'.local-preview/multicolor'
BASE = 'http://127.0.0.1:5173'
ID = 'yamaha-pacifica-612viifm'
report = {'checks':[], 'runtimeErrors':[], 'consoleErrors':[],
          'mobileReviewScreenshotWidth':390, 'mobileInteractionViewport':'390×844 in browser-gallery.py'}

def check(name, condition):
    report['checks'].append({'name':name,'passed':bool(condition)})
    print(('PASS ' if condition else 'FAIL ') + name, flush=True)
    assert condition, name

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
        page = browser.new_page(viewport={'width':1440,'height':1000},reduced_motion='reduce')
        page.on('pageerror',lambda e:report['runtimeErrors'].append(str(e)))
        page.on('console',lambda m:report['consoleErrors'].append(m.text) if m.type=='error' else None)
        page.goto(BASE+'/',wait_until='networkidle')
        card = page.locator('article[data-guitar-id="'+ID+'"]')
        expect(card).to_have_count(1)
        check('Homepage keeps one existing Pacifica card with the black image',card.locator('[data-preview-image="black"]').count()==1)
        page.goto(BASE+'/brands',wait_until='networkidle')
        expect(page.locator('.brands-page')).to_be_visible()
        page.goto(BASE+'/brands/yamaha',wait_until='networkidle')
        expect(page.locator('h1')).to_have_text('Yamaha')
        check('Yamaha Brand Detail retains exactly twenty cards',page.locator('.brand-models-section article[data-guitar-id]').count()==20)
        check('Brand catalog retains one Pacifica ID and its black image',page.locator('article[data-guitar-id="'+ID+'"] [data-preview-image="black"]').count()==1)
        page.goto(BASE+'/find-my-guitar?type=electric&level=intermediate&style=rock&budget=high&priority=versatile',wait_until='networkidle')
        expect(page.locator('.quiz-results-page')).to_be_visible()
        check('Quiz results still resolve the existing Pacifica model and black image',page.locator('.quiz-results-page [data-development-image-preview="'+ID+'"][data-preview-image="black"]').count()==1)
        # Taller capture removes fixed bottom-navigation overlap from review images.
        # This changes only screenshot framing, not application CSS or image bytes.
        page.set_viewport_size({'width':390,'height':2000})
        page.goto(BASE+'/guitars/'+ID,wait_until='networkidle')
        for label,color in [('Black','black'),('Red','red'),('Blue / Teal','blue-teal'),(None,'all-colors')]:
            if label:page.get_by_role('radio',name=label,exact=True).click()
            else:page.locator('.gallery-thumbnails button').nth(3).click()
            image=page.locator('.gallery-main img');image.evaluate('(i)=>i.decode()')
            page.evaluate('document.activeElement?.blur();window.scrollTo(0,0)')
            rect=page.locator('.detail-hero').bounding_box()
            filename=('gallery-overview' if not label else 'detail-'+color)+'-mobile.png'
            page.screenshot(path=str(OUT/'screenshots'/filename),full_page=True,animations='disabled',
                            clip={'x':0,'y':0,'width':390,'height':math.ceil(rect['y']+rect['height'])})
        page.set_viewport_size({'width':390,'height':844})
        page.goto(BASE+'/guitars/'+ID,wait_until='networkidle')
        page.get_by_role('button',name='เปิดดูรูปขนาดใหญ่',exact=True).click()
        dialog=page.get_by_role('dialog');expect(dialog).to_be_visible()
        dialog.get_by_role('button',name='รูปถัดไป',exact=True).click()
        check('Mobile lightbox next button displays red and preserves contain sizing',
              dialog.locator('div.relative [data-preview-image="red"]').count()==1
              and dialog.locator('div.relative [data-preview-image="red"] img').evaluate('(i)=>getComputedStyle(i).objectFit')=='contain')
        page.keyboard.press('Escape');expect(dialog).to_have_count(0)
        expect(page.get_by_role('radio',name='Red',exact=True)).to_be_checked()
        check('Mobile lightbox returns to the same red selector state',True)
        check('Shared-page smoke checks have no console/runtime errors',not report['runtimeErrors'] and not report['consoleErrors'])
        browser.close()
    report['passed']=True
except Exception:
    report['passed']=False;report['failure']=traceback.format_exc();print(report['failure'],flush=True)
finally:(OUT/'integration-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
