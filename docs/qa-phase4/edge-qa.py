from playwright.sync_api import sync_playwright,expect
from pathlib import Path
import json,os,traceback
OUTPUT=Path(__file__).resolve().parent
BASE=os.environ.get('FRETLINE_DEV_URL','http://127.0.0.1:5177')
report={'checks':[],'page_errors':[],'fixture_note':'Empty catalog is simulated only in this isolated browser memory; source files and production data are unchanged.'}
def check(name,condition=True):report['checks'].append({'name':name,'passed':bool(condition)});print(name,bool(condition),flush=True);assert condition,name
try:
 with sync_playwright() as p:
  browser=p.chromium.launch(executable_path=os.environ.get('CHROMIUM_BIN','/usr/bin/chromium'),args=['--no-sandbox'])
  page=browser.new_page(viewport={'width':390,'height':844})
  page.on('pageerror',lambda error:report['page_errors'].append(str(error)))
  page.goto(BASE+'/find-my-guitar',wait_until='networkidle')
  page.evaluate('''async()=>{
    const data=await import('/src/data/guitars.js');
    data.GUITARS.splice(0);
    window.history.pushState({},'', '/find-my-guitar?type=acoustic&level=intermediate&style=folk&budget=flex&priority=versatile');
    window.dispatchEvent(new PopStateEvent('popstate'));
  }''')
  expect(page.get_by_role('heading',name='ยังไม่มีรุ่นที่ได้คะแนนถึงเกณฑ์',exact=True)).to_be_visible()
  check('Results render genuine empty state without assuming a top model',page.locator('.match-card').count()==0)
  page.screenshot(path=str(OUTPUT/'quiz-empty-mobile.png'),animations='disabled')
  page.get_by_role('button',name='แก้ไขคำตอบ',exact=True).first.click();expect(page.locator('input[value="acoustic"]')).to_be_checked();check('Empty results can edit prior answers')
  page.reload(wait_until='networkidle')
  page.goto(BASE+'/find-my-guitar?type=acoustic&level=intermediate&style=folk&budget=flex&priority=versatile',wait_until='networkidle')
  expect(page.locator('.match-card')).to_have_count(3);check('Reload restores real catalog; fixture is not persisted')
  page.evaluate('Object.defineProperty(navigator,"clipboard",{configurable:true,value:{writeText:async()=>{throw new Error("denied")}}})')
  page.get_by_role('button',name='แชร์ลิงก์',exact=True).click();field=page.get_by_role('textbox',name='เลือกลิงก์นี้เพื่อคัดลอก');expect(field).to_be_visible()
  check('Quiz share fallback contains complete validated answers','priority=versatile' in field.input_value() and 'step=' not in field.input_value())
  page.goto(BASE+'/compare?ids=yamaha-fg830',wait_until='networkidle')
  page.get_by_role('button',name='เพิ่มกีตาร์',exact=True).first.click();dialog=page.get_by_role('dialog',name='เพิ่มกีตาร์',exact=True)
  dialog.get_by_role('searchbox').fill('no-such-model-zz')
  expect(dialog.get_by_text('ไม่พบรุ่นที่ตรงกับคำค้น',exact=True)).to_be_visible();check('Picker search empty state')
  page.keyboard.press('Escape');expect(dialog).not_to_be_visible()
  page.get_by_role('button',name='นำ FG830 ออกจากการเปรียบเทียบ',exact=True).click()
  expect(page.get_by_role('heading',name='เริ่มต้นด้วยกีตาร์ที่คุณสนใจ')).to_be_visible();check('Single selected guitar can be removed')
  check('Edge cases have no runtime errors',not report['page_errors'])
  browser.close()
 report['passed']=True
except Exception:
 report['passed']=False;report['failure']=traceback.format_exc();print(report['failure'],flush=True)
finally:(OUTPUT/'edge-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2))
if not report['passed']:raise SystemExit(1)
