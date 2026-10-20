"""Phase 7 browser checks: 200-model quotas, new records and preserved archive links."""
from pathlib import Path
from playwright.sync_api import sync_playwright, expect
import json, os, re, traceback

OUT=Path(__file__).resolve().parent
BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:4187')
DEV=os.environ.get('FRETLINE_QA_DEV_URL','http://127.0.0.1:5188')
DATA=json.loads((OUT.parent.parent/'src/data/catalog/phase7Guitars.json').read_text())
BRANDS=['Yamaha','Fender','Epiphone','Ibanez','Taylor','Córdoba','Gibson','Martin','PRS','Squier']
C40='yamaha-c40';G2420='gretsch-g2420-streamliner';NEW='fender-player-ii-telecaster';PHOTO='yamaha-fg820-12'
report={'checks':[],'page_errors':[],'console_errors':[],'failed_requests':[],'screenshots':[]}

def check(name,condition=True):
    report['checks'].append({'name':name,'passed':bool(condition)})
    print(name,bool(condition),flush=True)
    assert condition,name

def visit(page,path,base=BASE):page.goto(base+path,wait_until='networkidle')
def stored(page,key):return page.evaluate('(key)=>JSON.parse(localStorage.getItem("fretline:"+key)||"[]")',key)
def shot(page,name,full=True):
    page.screenshot(path=str(OUT/name),full_page=full,animations='disabled')
    report['screenshots'].append(name)
def count(page,key,n):page.wait_for_function('({key,n})=>JSON.parse(localStorage.getItem("fretline:"+key)||"[]").length===n',arg={'key':key,'n':n})

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
        page=browser.new_page(viewport={'width':1440,'height':1100})
        page.set_default_timeout(12000)
        page.on('pageerror',lambda error:report['page_errors'].append(str(error)))
        page.on('console',lambda message:report['console_errors'].append(message.text) if message.type=='error' else None)
        page.on('requestfailed',lambda request:report['failed_requests'].append({'url':request.url,'failure':request.failure}))
        visit(page,'/brands')
        cards=page.locator('.brand-directory-card')
        expect(cards).to_have_count(10)
        counts=page.locator('.brand-card-count').all_text_contents()
        check('Brands directory has exactly ten brands with twenty models each',len(counts)==10 and all(int(re.search(r'\d+',x)[0])==20 for x in counts))
        check('Gretsch is absent from active brand cards',cards.locator('[data-brand-id="gretsch"]').count()==0 and page.locator('[data-brand-id="gretsch"]').count()==0)
        shot(page,'brands-200-desktop.png')
        for brand in BRANDS:
            visit(page,'/guitars?brand='+brand)
            check('Catalog brand filter has twenty models: '+brand,'20' in page.locator('.catalog-results').inner_text() and page.locator('.catalog-grid article').count()==9)
            page.get_by_role('button',name='หน้าถัดไป',exact=True).click()
            page.get_by_role('button',name='หน้าถัดไป',exact=True).click()
            expect(page.locator('.catalog-grid article')).to_have_count(2)
            check('Brand pagination ends at two models on page three: '+brand,'page=3' in page.url)
        visit(page,'/guitars')
        expect(page.locator('.catalog-grid article')).to_have_count(9)
        expect(page.get_by_role('button',name='หน้า 23',exact=True)).to_be_visible()
        check('200 models produce 23 functional nine-item pages')
        shot(page,'catalog-200-desktop.png')
        page.get_by_role('button',name='หน้า 23',exact=True).click()
        expect(page.locator('.catalog-grid article')).to_have_count(2)
        expect(page.get_by_role('button',name='หน้าถัดไป',exact=True)).to_be_disabled()
        check('Final catalog page has exactly the final two real records')
        page.go_back(wait_until='networkidle')
        expect(page.locator('.catalog-grid article')).to_have_count(9)
        page.go_forward(wait_until='networkidle')
        expect(page.locator('.catalog-grid article')).to_have_count(2)
        check('Catalog Back and Forward retain the enlarged pagination')
        for query in ['C40','G2420']:
            visit(page,'/guitars?q='+query)
            expect(page.locator('.catalog-grid article')).to_have_count(0)
            check('Archived model is absent from catalog search: '+query)
        # One new product per added brand, across all renderer/specification shapes.
        representatives=[next(g for g in DATA if g['brand']==brand) for brand in BRANDS if brand!='Yamaha']
        for guitar in representatives:
            visit(page,'/guitars/'+guitar['id'])
            expect(page.locator('.detail-summary h1')).to_have_text(guitar['name'])
            page.get_by_role('tab',name='สเปก',exact=True).click()
            text=page.locator('#specs .spec-table').inner_text()
            check('New real model renders sourced facts and unknown price: '+guitar['brand'],guitar['specs']['body'] in text and 'ยังไม่มีข้อมูลราคา' in text and 'ไม่ระบุ' in text)
            page.locator('#specs .source-scope summary').click()
            check('Source limitations are disclosed: '+guitar['brand'],'ยังไม่ยืนยัน' in page.locator('#specs .source-scope').inner_text() or 'ตรวจ' in page.locator('#specs .source-scope').inner_text())
        visit(page,'/guitars/prs-se-mccarty-594-singlecut')
        page.locator('.detail-summary .source-scope summary').click()
        check('PRS PDF year and page are explicit, not represented as all-year specs','2025' in page.locator('.source-scope').first.inner_text() and 'หน้า 3' in page.locator('.source-scope').first.inner_text())
        # Simulate a real old saved collection. Reloading initializes the shared context.
        page.evaluate('([a,b,c])=>{localStorage.setItem("fretline:wishlist",JSON.stringify([a,b,a,c]));localStorage.setItem("fretline:compare",JSON.stringify([a,b]))}',[C40,G2420,NEW])
        visit(page,'/wishlist')
        count(page,'wishlist',3);count(page,'compare',2)
        check('Old saved archive IDs remain intact, with duplicates removed',stored(page,'wishlist')==[C40,G2420,NEW])
        expect(page.locator('.wishlist-row')).to_have_count(3)
        check('Wishlist explicitly labels both archived rows',page.locator('.wishlist-row .archive-label').count()==2 and page.locator('.archive-notice').count()==1)
        shot(page,'wishlist-archive-desktop.png')
        for archived in [C40,G2420]:
            page.locator(f'.wishlist-row[data-guitar-id="{archived}"] [data-wishlist-detail]').click()
            expect(page.locator('.detail-summary h1')).to_be_visible()
            check('Old saved detail link remains accessible and marked archived: '+archived,'ไม่รวมในยอด 200 รุ่น' in page.locator('.archive-notice').inner_text())
            page.go_back(wait_until='networkidle')
        page.reload(wait_until='networkidle')
        check('Reload never silently deletes the two archived favourites',stored(page,'wishlist')==[C40,G2420,NEW])
        visit(page,'/compare?ids='+C40+','+G2420+','+C40+','+NEW)
        count(page,'compare',3)
        check('Legacy shared comparison URL preserves archive IDs and deduplicates',stored(page,'compare')==[C40,G2420,NEW])
        check('Comparison and shared tray render archive labels and all three names',page.locator('.compare-table-scroll .archive-label').count()==2 and 'C40' in page.locator('.compare-table-scroll').inner_text() and 'G2420' in page.locator('.compare-table-scroll').inner_text())
        shot(page,'compare-archive-desktop.png')
        page.locator('.compare-table-scroll').get_by_role('button',name='นำ C40 Classical ออกจากการเปรียบเทียบ',exact=True).click()
        count(page,'compare',2)
        check('User can remove an archived comparison without losing favourites',stored(page,'compare')==[G2420,NEW] and len(stored(page,'wishlist'))==3)
        page.go_back(wait_until='networkidle');count(page,'compare',3)
        check('Compare Browser Back restores archived shared selection',stored(page,'compare')==[C40,G2420,NEW])
        page.go_forward(wait_until='networkidle');count(page,'compare',2)
        check('Compare Browser Forward restores removal',stored(page,'compare')==[G2420,NEW])
        visit(page,'/brands/gretsch')
        expect(page.locator('h1')).to_have_text('Gretsch')
        check('Old Gretsch brand link explains archival instead of a broken route',page.locator('.archive-notice').count()==1 and page.get_by_role('link',name=re.compile('Gretsch G2420')).count()==1)
        visit(page,'/wishlist')
        remove=page.locator(f'.wishlist-row[data-guitar-id="{C40}"]').get_by_role('button',name=re.compile('^นำ .*ออกจากรายการโปรด'))
        remove.focus();page.keyboard.press('Enter');count(page,'wishlist',2)
        check('Only an explicit user action removes an archived favourite',stored(page,'wishlist')==[G2420,NEW])
        visit(page,'/find-my-guitar?type=classical&level=beginner&style=classical&budget=mid&priority=value')
        results=page.locator('.match-card')
        expect(results.first).to_be_visible()
        check('Quiz recommends active records and excludes archived C40','C40' not in page.locator('.quiz-results-page').inner_text() and page.locator('.quiz-results-page a[href="/guitars/yamaha-c40"]').count()==0)
        # Responsive route checks include long new names and archive notices.
        paths=[('catalog-200','/guitars'),('brands-200','/brands'),('new-detail','/guitars/epiphone-es-335-figured-with-rosewood-fretboard'),('archive-detail','/guitars/'+C40),('archive-brand','/brands/gretsch'),('compare-archive','/compare?ids='+C40+','+G2420+','+NEW),('wishlist-archive','/wishlist')]
        for label,width,height in [('tablet',768,1024),('mobile',390,844)]:
            page.set_viewport_size({'width':width,'height':height})
            for name,path in paths:
                visit(page,path)
                expect(page.locator('main h1')).to_be_visible()
                check(name+' '+label+' has no document overflow',page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
                shot(page,name+'-'+label+'.png')
                if name=='compare-archive' and label=='mobile':
                    region=page.locator('.compare-table-scroll')
                    region.focus();page.keyboard.press('ArrowRight')
                    page.wait_for_function('()=>document.querySelector(".compare-table-scroll").scrollLeft>0')
                    check('Mobile comparison table scrolls horizontally with the keyboard')
        page.set_viewport_size({'width':320,'height':800})
        for path in ['/guitars/'+C40,'/brands/gretsch','/wishlist','/guitars/epiphone-es-335-figured-with-rosewood-fretboard']:
            visit(page,path)
            check('320px archive/new route has no overflow: '+path,page.evaluate('document.documentElement.scrollWidth<=innerWidth+1'))
        # Strict Mode development view must reconcile the same old shared IDs.
        visit(page,'/compare?ids='+G2420+','+C40,DEV)
        count(page,'compare',2)
        check('Dev Strict Mode retains old shared archive IDs',stored(page,'compare')==[G2420,C40])
        page.reload(wait_until='networkidle')
        check('Dev Strict Mode reload does not drop or reorder archive IDs',stored(page,'compare')==[G2420,C40])
        check('No runtime or page errors',not report['page_errors'])
        check('No console errors',not report['console_errors'])
        check('No failed normal-flow requests',not report['failed_requests'])
        browser.close()

try:
    run();report['passed']=True
except Exception:
    report['passed']=False;report['failure']=traceback.format_exc();print(report['failure'],flush=True)
finally:
    (OUT/'browser-phase7-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
if not report['passed']:raise SystemExit(1)
