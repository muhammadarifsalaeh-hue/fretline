"""Viewport captures of paired/stacked banners and the three real Hero scenes."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import argparse, hashlib, json, re

ROOT = Path(__file__).resolve().parents[3]
p = argparse.ArgumentParser()
p.add_argument('--url', default='http://127.0.0.1:5451')
args = p.parse_args()
OUT = ROOT / 'docs/home-editorial-refinement/screenshots'
OUT.mkdir(parents=True, exist_ok=True)
snapshot = lambda: {str(f.relative_to(ROOT)): hashlib.sha256(f.read_bytes()).hexdigest()
                    for prefix in ['src', 'dist'] for f in (ROOT / prefix).rglob('*') if f.is_file()}
before = snapshot()
catalog=json.loads((ROOT/'docs/home-editorial-refinement/tests/catalog-fixture.json').read_text())
report = {'screenshots': [], 'errors': [], 'viewports': [], 'physicalIPadSafariTested': False,
          'sourceAndBuildSHA256': before}

with sync_playwright() as p:
    browser = p.chromium.launch(executable_path='/usr/bin/chromium', args=['--no-sandbox'])
    for label, width, height in [('desktop',1440,1000),('tablet',768,1024),('landscape',1194,834),('mobile',390,844)]:
        context = browser.new_context(viewport={'width':width,'height':height}, reduced_motion='reduce', has_touch=width<1024)
        page = context.new_page()
        page.on('pageerror', lambda e: report['errors'].append(str(e)))
        page.on('console', lambda m: report['errors'].append(m.text) if m.type=='error' else None)
        page.goto(args.url, wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        category_counts={kind:sum(g['category']==kind for g in catalog) for kind in ['electric','acoustic','classical','bass']}
        for kind,count in category_counts.items():
            text=page.locator('.signature-category-card[href="/guitars?type='+kind+'"] p').inner_text()
            assert int(re.search(r'\d+',text).group())==count,(kind,count,text)
        pair = page.locator('.home-editorial-pair')
        for im in pair.locator('img').all():
            im.scroll_into_view_if_needed()
            im.evaluate('(i)=>i.decode()')
        pair.evaluate("e=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-14)")
        name=label+'-editorial-pair.png'
        page.screenshot(path=str(OUT/name), animations='disabled')
        report['screenshots'].append(name)
        metrics=page.evaluate('({width:innerWidth,scrollWidth:document.documentElement.scrollWidth})')
        assert metrics['scrollWidth']<=width+1, metrics
        find=page.locator('#find').bounding_box();compare=page.locator('#compare').bounding_box()
        if width>=1024:
            assert abs(find['y']-compare['y'])<=1 and find['x']+find['width']<=compare['x'],(find,compare)
        else:
            assert find['y']+find['height']<=compare['y'],(find,compare)
        report['viewports'].append({'label':label,'layout':'paired' if width>=1024 else 'stacked','find':find,'compare':compare,**metrics})
        featured=page.locator('#featured')
        for im in featured.locator('img').all():
            im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()')
        # Decoding an offscreen product can move native horizontal scroll. Restore
        # the real initial left edge before the default-state delivery capture.
        page.locator('.signature-collection-track').evaluate('(e)=>e.scrollLeft=0')
        featured.evaluate("e=>scrollBy(0,e.getBoundingClientRect().top-document.querySelector('.site-header').getBoundingClientRect().height-14)")
        name=label+'-featured.png';page.screenshot(path=str(OUT/name),animations='disabled');report['screenshots'].append(name)
        if label=='desktop':
            page.evaluate('scrollTo(0,0)')
            for index in range(3):
                expect(page.locator('#top')).to_have_attribute('data-hero-slide-index',str(index))
                page.locator('.signature-hero-slide').nth(index).locator('img').evaluate('(i)=>i.decode()')
                name='desktop-hero-slide-'+str(index+1)+'.png'
                page.screenshot(path=str(OUT/name),animations='disabled')
                report['screenshots'].append(name)
                if index<2:
                    page.mouse.move(1200,190)
                    page.mouse.down()
                    page.mouse.move(1000,190,steps=10)
                    page.mouse.up()
        context.close()
    browser.close()

report['sourceAndBuildUnchangedDuringRun']=before==snapshot()
report['passed']=not report['errors'] and report['sourceAndBuildUnchangedDuringRun'] and len(report['screenshots'])==11
(OUT/'capture-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('Delivery viewport captures:',report['passed'],len(report['screenshots']))
assert report['passed'],report
