"""Render the proposal document; this does not test a redesigned application."""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json,os

OUT=Path(__file__).resolve().parent
URL=os.environ.get('FRETLINE_PROPOSAL_URL','http://127.0.0.1:5202/docs/signature-redesign/phase-c-proposal/homepage.html')
report={'scope':'Documentation-only Phase C homepage mockup; application unchanged; not Safari results',
        'views':[],'consoleErrors':[],'runtimeErrors':[],'failedRequests':[]}
with sync_playwright() as playwright:
    browser=playwright.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
    for width,height,label in [(1440,1000,'desktop'),(390,844,'mobile'),(768,1024,'tablet'),(1024,768,'ipad-landscape'),(320,740,'small-mobile')]:
        context=browser.new_context(viewport={'width':width,'height':height},reduced_motion='reduce')
        page=context.new_page()
        page.on('console',lambda msg:report['consoleErrors'].append(msg.text) if msg.type=='error' else None)
        page.on('pageerror',lambda error:report['runtimeErrors'].append(str(error)))
        page.on('requestfailed',lambda req:report['failedRequests'].append({'url':req.url,'failure':req.failure}))
        page.goto(URL,wait_until='networkidle')
        page.evaluate('document.fonts.ready')
        # Trigger native lazy loading by real scrolling, preserving image files.
        offset=0
        while True:
            page.evaluate('(y)=>window.scrollTo(0,y)',offset)
            page.wait_for_timeout(40)
            bottom=page.evaluate('document.documentElement.scrollHeight')
            if offset+height>=bottom:break
            offset=min(offset+int(height*.8),bottom-height)
        page.wait_for_function('[...document.images].every(img=>img.complete&&img.naturalWidth>0)')
        page.evaluate('async()=>{await Promise.all([...document.images].map(img=>img.decode()));window.scrollTo(0,0);await new Promise(requestAnimationFrame)}')
        metrics=page.evaluate('''()=>({viewport:innerWidth,scrollWidth:document.documentElement.scrollWidth,
          cards:[...document.querySelectorAll('.product')].map(card=>({id:card.dataset.guitarId,name:card.querySelector('h3').textContent,imageFit:getComputedStyle(card.querySelector('img')).objectFit})),
          brands:document.querySelectorAll('.brand-grid>a').length,
          h1:document.querySelector('h1').textContent,
          brokenImages:[...document.images].filter(img=>img.complete&&!img.naturalWidth).map(img=>img.currentSrc)})''')
        assert metrics['scrollWidth']<=width+1,metrics
        assert metrics['brands']==10 and len(metrics['cards'])==3,metrics
        assert all(card['imageFit']=='contain' for card in metrics['cards']),metrics
        assert not metrics['brokenImages'],metrics
        shots=[]
        if label in ['desktop','mobile','tablet']:
            for full in [False,True]:
                name=f'homepage-{label}'+('-full' if full else '')+'.png'
                page.screenshot(path=str(OUT/name),full_page=full,animations='disabled')
                shots.append(name)
        report['views'].append({'width':width,'height':height,'measurements':metrics,'screenshots':shots})
        print(f'PASS mockup {width}px: no overflow;3 model images;10 brand links',flush=True)
        context.close()
    browser.close()
report['passed']=not report['consoleErrors'] and not report['runtimeErrors'] and not report['failedRequests']
(OUT/'render-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
