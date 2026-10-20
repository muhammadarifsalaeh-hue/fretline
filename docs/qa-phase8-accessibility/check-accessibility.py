"""Reproducible axe-core WCAG audit; testing tool is external to app dependencies.
Download axe-core 4.10.3 to /tmp/fretline-axe.min.js before running.
FRETLINE_QA_URL defaults to local dev; pass production preview for final audit.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json, os
OUT = Path(__file__).parent
BASE = os.environ.get('FRETLINE_QA_URL', 'http://127.0.0.1:5189')
report = {'engine':'axe-core 4.10.3', 'browser':'Chromium on Linux; not Safari', 'routes':[]}
routes = [('/', 'home'),('/guitars','catalog'),('/guitars/fender-player-ii-telecaster','detail'),('/guitars/yamaha-fg820-12','photo-detail'),('/compare?ids=yamaha-fg820-12,fender-player-ii-telecaster','compare'),('/find-my-guitar','quiz-welcome'),('/find-my-guitar?type=acoustic&step=1','quiz-step'),('/find-my-guitar?type=acoustic&level=intermediate&style=folk&budget=mid&priority=versatile','quiz-results'),('/brands','brands'),('/brands/yamaha','brand-detail'),('/wishlist','wishlist'),('/image-credits','image-credits')]
with sync_playwright() as p:
    browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
    page=browser.new_page(reduced_motion='reduce')
    page.goto(BASE,wait_until='networkidle')
    page.evaluate('localStorage.setItem("fretline:wishlist",JSON.stringify(["yamaha-fg820-12","fender-player-ii-telecaster","yamaha-c40"]))')
    for width,height in [(1440,1000),(390,844)]:
        page.set_viewport_size({'width':width,'height':height})
        for path,name in routes:
            page.goto(BASE+path,wait_until='networkidle')
            page.add_script_tag(path='/tmp/fretline-axe.min.js')
            result=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,help:v.help,helpUrl:v.helpUrl,nodes:v.nodes.map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary}))})),passes:r.passes.length,incomplete:r.incomplete.map(x=>({id:x.id,nodes:x.nodes.length}))}}''')
            report['routes'].append({'route':path,'name':name,'width':width,**result})
            print(name,width,[(v['id'],len(v['nodes'])) for v in result['violations']],flush=True)
    # Audit modal states too: route-only audits cannot inspect open dialogs.
    page.set_viewport_size({'width':390,'height':844})
    states = [
        ('/', 'mobile-navigation', 'เปิดเมนู'),
        ('/guitars', 'mobile-filters', 'ตัวกรอง'),
        ('/compare?ids=yamaha-fg820-12,fender-player-ii-telecaster', 'compare-picker', 'เพิ่มกีตาร์'),
        ('/compare?ids=yamaha-fg820-12,fender-player-ii-telecaster', 'clear-confirmation', 'ล้างการเปรียบเทียบ'),
        ('/guitars/yamaha-fg820-12', 'photo-lightbox', 'เปิดดูรูปขนาดใหญ่'),
    ]
    for path,name,button in states:
        page.goto(BASE+path,wait_until='networkidle')
        page.get_by_role('button',name=button,exact=True).click()
        page.locator('[role="dialog"]:visible, [role="alertdialog"]:visible').first.wait_for(state='visible')
        page.add_script_tag(path='/tmp/fretline-axe.min.js')
        result=page.evaluate('''async()=>{const r=await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21a','wcag21aa']}});return {violations:r.violations.map(v=>({id:v.id,impact:v.impact,description:v.description,help:v.help,helpUrl:v.helpUrl,nodes:v.nodes.map(n=>({target:n.target,html:n.html,failureSummary:n.failureSummary}))})),passes:r.passes.length,incomplete:r.incomplete.map(x=>({id:x.id,nodes:x.nodes.length}))}}''')
        report['routes'].append({'route':path,'name':name,'state':'dialog open','width':390,**result})
        print(name,390,[(v['id'],len(v['nodes'])) for v in result['violations']],flush=True)
    report['violations']=sum(len(r['violations']) for r in report['routes'])
    report['passed']=report['violations']==0
    browser.close()
(OUT/'accessibility-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
raise SystemExit(0 if report['passed'] else 1)
