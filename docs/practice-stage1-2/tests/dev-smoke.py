"""Actual browser smoke of Vite dev + a native production workspace capture."""
from pathlib import Path
import json
import os
import traceback
from playwright.sync_api import sync_playwright,expect

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'docs/practice-stage1-2'
PRODUCTION=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:5410').rstrip('/')
DEV=os.environ.get('FRETLINE_QA_DEV_URL','http://127.0.0.1:5412').rstrip('/')
ENGINE=os.environ.get('FRETLINE_QA_ENGINE','chromium')
REPORT={'engine':ENGINE,'productionURL':PRODUCTION,'devURL':DEV,'consoleErrors':[],
        'runtimeErrors':[],'failedRequests':[],
        'limitations':['Linux browser engine, not physical iPad Safari.',
                        'Chromium uses SwiftShader software rendering.' if ENGINE=='chromium' else 'Linux WebKit WPE does not reproduce the iPad GPU.',
                        'Dev URL smoke does not validate GitHub Codespaces port forwarding.']}


def wait_changed(page,before):
    page.wait_for_function('''old=>{const raw=document.querySelector('canvas[data-practice-canvas]')?.dataset.camera;
      if(!raw)return false;return JSON.parse(raw).position.some((value,i)=>Math.abs(value-old.position[i])>.0001)}''',arg=before)


try:
    with sync_playwright() as p:
        if ENGINE=='webkit': browser=p.webkit.launch()
        elif ENGINE=='chromium': browser=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader'])
        else: raise ValueError(ENGINE)
        REPORT['browserVersion']=browser.version
        context=browser.new_context(viewport={'width':1440,'height':1600},locale='th-TH',reduced_motion='reduce')
        page=context.new_page()
        page.on('console',lambda message:REPORT['consoleErrors'].append(message.text) if message.type=='error' else None)
        page.on('pageerror',lambda error:REPORT['runtimeErrors'].append(str(error)))
        page.on('requestfailed',lambda request:REPORT['failedRequests'].append({'url':request.url,'failure':request.failure}))
        page.goto(PRODUCTION+'/practice',wait_until='networkidle')
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=30000)
        expect(page.locator('canvas[data-practice-canvas]')).to_have_attribute('data-chord-id','C')
        page.evaluate('document.fonts.ready')
        shot=OUT/'screenshots'/ENGINE/'workspace-desktop.png';shot.parent.mkdir(parents=True,exist_ok=True)
        page.locator('.practice-workspace').screenshot(path=str(shot),animations='allow')
        REPORT['productionWorkspaceCapture']={'path':str(shot.relative_to(OUT)),'viewport':{'width':1440,'height':1600},'method':'Native element screenshot of actual workspace, no DOM/CSS replacements.'}
        page.set_viewport_size({'width':1024,'height':768})
        page.goto(DEV+'/practice',wait_until='networkidle')
        expect(page.locator('[data-practice-status]')).to_have_attribute('data-practice-status','ready',timeout=45000)
        canvas=page.locator('canvas[data-practice-canvas]')
        assert canvas.get_attribute('data-string-count')=='6' and canvas.get_attribute('data-fret-count')=='12'
        assert canvas.evaluate('c=>Boolean(c.getContext("webgl2"))')
        initial=json.loads(canvas.get_attribute('data-camera'))
        page.locator('[data-practice-chord="G"]').click()
        expect(canvas).to_have_attribute('data-chord-id','G')
        page.get_by_role('button',name='หมุนไปทางซ้าย',exact=True).click();wait_changed(page,initial)
        rotated=json.loads(canvas.get_attribute('data-camera'))
        page.get_by_role('button',name='ซูมเข้า',exact=True).click();wait_changed(page,rotated)
        zoomed=json.loads(canvas.get_attribute('data-camera'));assert zoomed['distance']<rotated['distance']
        page.get_by_role('button',name='รีเซ็ตกล้อง',exact=True).click()
        page.wait_for_function('''old=>{const now=JSON.parse(document.querySelector('canvas[data-practice-canvas]').dataset.camera);return now.position.every((value,i)=>Math.abs(value-old.position[i])<.0001)}''',arg=initial)
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        REPORT['devChecks']={'actualWebGL2':True,'strings':6,'frets':12,'selectedChord':'G','rotateWorks':True,'zoomWorks':True,'resetWorks':True,'noPageOverflow':True}
        browser.close()
    REPORT['passed']=not any(REPORT[key] for key in ['consoleErrors','runtimeErrors','failedRequests'])
except Exception:
    REPORT['passed']=False;REPORT['failure']=traceback.format_exc();print(REPORT['failure'],flush=True)
finally:
    (OUT/('dev-smoke-'+ENGINE+'.json')).write_text(json.dumps(REPORT,ensure_ascii=False,indent=2)+'\n')
print(('PASS' if REPORT['passed'] else 'FAIL')+' '+ENGINE+' production-workspace and Vite-dev-smoke',flush=True)
raise SystemExit(0 if REPORT['passed'] else 1)
