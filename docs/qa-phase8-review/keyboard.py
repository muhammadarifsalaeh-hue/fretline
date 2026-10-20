"""Dialog focus and keyboard regressions, including the persistent mobile drawer."""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import os,json
OUT=Path(__file__).parent;BASE=os.environ.get('FRETLINE_QA_URL','http://127.0.0.1:4188')
r={'checks':[],'page_errors':[],'console_errors':[]}
def check(name,condition=True):
 r['checks'].append({'name':name,'passed':bool(condition)});print(name,bool(condition),flush=True);assert condition,name
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 for motion in ['reduce','no-preference']:
  pg=b.new_page(viewport={'width':390,'height':844},reduced_motion=motion)
  pg.on('pageerror',lambda e:r['page_errors'].append(str(e)));pg.on('console',lambda m:r['console_errors'].append(m.text) if m.type=='error' else None)
  pg.goto(BASE+'/guitars',wait_until='networkidle');trigger=pg.locator('.catalog-filter-trigger');trigger.click()
  dialog=pg.locator('#catalog-filter-dialog');expect(dialog.get_by_role('button',name='ปิดตัวกรอง',exact=True)).to_be_focused(timeout=3000)
  check('Drawer autofocus enters the newly visible dialog: '+motion)
  pg.keyboard.press('Shift+Tab');expect(dialog.get_by_role('button',name='แสดง 200 รุ่น',exact=True)).to_be_focused()
  pg.keyboard.press('Tab');expect(dialog.get_by_role('button',name='ปิดตัวกรอง',exact=True)).to_be_focused()
  check('Drawer wraps forward and backward Tab inside the dialog: '+motion)
  pg.keyboard.press('Escape');expect(trigger).to_be_focused();check('Escape returns focus and releases body scroll: '+motion,pg.evaluate('document.body.style.overflow')=='')
  trigger.click();expect(dialog.get_by_role('button',name='ปิดตัวกรอง',exact=True)).to_be_focused(timeout=3000)
  pg.set_viewport_size({'width':1024,'height':768});pg.wait_for_function('()=>document.body.style.overflow!=="hidden"')
  check('Switching to desktop closes drawer and releases scroll: '+motion)
  pg.set_viewport_size({'width':390,'height':844});menu=pg.get_by_role('button',name='เปิดเมนู',exact=True);menu.click()
  pg.wait_for_function('()=>document.querySelector("#mobile-navigation").contains(document.activeElement)')
  pg.keyboard.press('Escape');expect(menu).to_be_focused();check('Mobile menu Escape restores the opener: '+motion)
  pg.goto(BASE+'/',wait_until='networkidle')
  tab=pg.locator('#featured-tab-all');tab.focus();pg.keyboard.press('ArrowRight');expect(pg.locator('#featured-tab-electric')).to_be_focused()
  expect(pg.locator('#featured-tab-electric')).to_have_attribute('aria-selected','true')
  check('Home featured tabs support arrow-key selection: '+motion)
  pg.close()
 r['passed']=all(c['passed'] for c in r['checks']) and not r['page_errors'] and not r['console_errors'];b.close()
(OUT/'keyboard-results.json').write_text(json.dumps(r,ensure_ascii=False,indent=2)+'\n')
