"""Real AdminEditor UI, codec and gallery resolver; in-memory Storage/RPC fixtures.
No live Supabase, auth/RLS claims or changes to real product records.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright,expect
import json,traceback
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
report={'scope':'actual image UI/codec with explicit in-memory service fixtures','hostedSupabaseTested':False,'physicalIPadTested':False,'realDatabaseWrites':0,'checks':[],'errors':[]}
current='start'
def passed(name,detail=None):
 report['checks'].append({'name':name,'passed':True,'evidence':detail});print('PASS',name,flush=True)
def square_frames(page,selector):
 result=page.locator(selector).evaluate_all('(es)=>es.map(e=>({w:e.getBoundingClientRect().width,h:e.getBoundingClientRect().height,bg:getComputedStyle(e).backgroundColor}))')
 assert result and all(abs(e['w']-e['h'])<1.5 and e['bg']=='rgb(0, 0, 0)' for e in result),result
 return result
expect.set_options(timeout=15000)
with sync_playwright() as p:
 b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox'])
 c=b.new_context(viewport={'width':1194,'height':834},has_touch=True,reduced_motion='reduce');page=c.new_page();page.on('pageerror',lambda e:report['errors'].append(str(e)));page.on('dialog',lambda d:d.accept())
 page.add_init_script('''const make=URL.createObjectURL.bind(URL),remove=URL.revokeObjectURL.bind(URL);window.__blobAudit={created:[],revoked:[]};URL.createObjectURL=(b)=>{const u=make(b);__blobAudit.created.push(u);return u};URL.revokeObjectURL=(u)=>{__blobAudit.revoked.push(u);return remove(u)};''')
 try:
  page.goto('http://127.0.0.1:4194/docs/universal-guitar-images/harness.html',wait_until='networkidle');expect(page.get_by_role('heading',name='ทดสอบส่วนแสดงภาพเท่านั้น')).to_be_visible()
  page.locator('.admin-tabs').get_by_role('button',name='รูปภาพ',exact=True).click()
  current='selection-is-local-and-formats';field=page.locator('input[type=file]');expect(field).to_be_disabled()
  page.get_by_label('ฉันมีสิทธิ์ใช้ภาพเหล่านี้ และภาพตรงกับรุ่นนี้',exact=True).check()
  paths=[ROOT/'src/assets/guitars/yamaha-fg800/01-supplied-yamaha-fg800-natural.webp',ROOT/'src/assets/guitars/yamaha-fg800m/01-supplied-yamaha-fg800m-natural-black-background.png',ROOT/'src/assets/guitars/yamaha-fg800j/01-supplied-yamaha-fg800j-natural.jpg']
  with page.expect_file_chooser() as chooser:
   page.get_by_text('เลือกภาพจาก Photos หรือ Files',exact=True).click()
  chooser.value.set_files([str(p) for p in paths]);expect(page.locator('[data-upload-status=ready]')).to_have_count(3,timeout=30000)
  assert page.evaluate('__imageFixture.uploads.length')==0
  expect(page.get_by_role('button',name='เผยแพร่',exact=True)).to_be_disabled()
  for im in page.locator('.admin-upload-queue img').all():im.evaluate('(i)=>i.decode()');assert im.evaluate('(i)=>i.naturalWidth===1200&&i.naturalHeight===1200')
  page.locator('.admin-tabs').get_by_role('button',name='ราคา',exact=True).click();page.locator('.admin-tabs').get_by_role('button',name='รูปภาพ',exact=True).click();expect(page.locator('[data-upload-status=ready]')).to_have_count(3)
  passed(current,{'inputFormats':['WebP','PNG','JPEG'],'preparedDimensions':[1200,1200],'uploadRequestsBeforeConfirmation':0,'stagedFilesSurviveTabSwitch':True})
  current='preview-responsive-four-types'
  (OUT/'screenshots').mkdir(exist_ok=True)
  for name,w,h in [('desktop',1440,1000),('landscape',1194,834),('portrait',768,1024),('mobile',390,844)]:
   page.set_viewport_size({'width':w,'height':h});square_frames(page,'.admin-upload-queue .guitar-image-frame');square_frames(page,'.qa-types .guitar-image-frame')
   assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
   for im in page.locator('.qa-types img').all():im.scroll_into_view_if_needed();im.evaluate('(i)=>i.decode()');assert im.evaluate('(i)=>getComputedStyle(i).objectFit==="contain"&&getComputedStyle(i).transform==="none"&&i.getBoundingClientRect().width<=i.naturalWidth+1&&i.getBoundingClientRect().height<=i.naturalHeight+1')
   page.locator('.admin-image-upload').scroll_into_view_if_needed();page.locator('.admin-image-upload').screenshot(path=str(OUT/'screenshots'/('admin-preview-'+name+'.png')),animations='disabled')
  passed(current,{'viewports':4,'types':['electric','acoustic','classical','bass'],'categoryImagesUsedOnlyInIsolatedComponentTest':True})
  current='upload-id-cache-and-no-overwrite';page.set_viewport_size({'width':1194,'height':834});page.get_by_role('button',name='อัปโหลด 3 ภาพที่ตรวจแล้ว',exact=True).click()
  expect(page.locator('.admin-upload-queue')).to_have_count(0);expect(page.locator('.admin-images>li')).to_have_count(3)
  info=page.evaluate('''async()=>Promise.all(__imageFixture.uploads.map(async u=>{const i=await createImageBitmap(u.blob);return {path:u.path,type:u.blob.type,w:i.width,h:i.height,options:u.options}}))''')
  assert len({x['path'] for x in info})==3 and all(x['path'].startswith('qa-image-upload/') and not x['options']['upsert'] and x['options']['cacheControl']=='86400' and x['w']==x['h']==1200 for x in info),info
  assert page.evaluate('__imageFixture.row.published.gallery.length')==0
  passed(current,info)
  current='cover-save-draft-publish-and-catalog'
  page.locator('.admin-images>li').nth(2).get_by_role('button',name='ตั้งเป็นรูปปก',exact=True).click()
  page.get_by_role('button',name='บันทึกแบบร่าง',exact=True).click();expect(page.get_by_role('status').filter(has_text='บันทึกแบบร่างแล้ว')).to_be_visible()
  assert page.evaluate('__imageFixture.row.draft.gallery.length')==3 and page.evaluate('__imageFixture.row.published.gallery.length')==0
  expect(page.locator('.qa-published .image-placeholder')).to_be_visible()
  page.get_by_role('button',name='เผยแพร่',exact=True).click();expect(page.get_by_role('status').filter(has_text='เผยแพร่แล้ว')).to_be_visible();expect(page.locator('.qa-published img')).to_be_visible()
  assert page.evaluate('__imageFixture.row.published.gallery[0].originalName').endswith('.jpg')
  assert page.evaluate('__imageFixture.row.published.price')==12400
  assert page.evaluate('__imageFixture.row.published.specs.scaleMm')==650
  square_frames(page,'.qa-published .guitar-image-frame')
  passed(current,{'draftHiddenUntilPublish':True,'coverOrderPreserved':True,'realPublicResolverUsed':True,'catalogPlaceholderReplaced':True,'priceAndSpecsUnchanged':True,'fixtureOnly':True})
  current='invalid-format-rejected-before-storage'
  field.set_input_files({'name':'not-a-photo.heic','mimeType':'image/heic','buffer':b'not a product image'})
  expect(page.locator('[data-upload-status=error]')).to_have_count(1);expect(page.get_by_role('alert').filter(has_text='รองรับ JPG')).to_be_visible();assert page.evaluate('__imageFixture.uploads.length')==3
  page.get_by_role('button',name='นำออกจากรายการอัปโหลด',exact=True).click();passed(current)
  current='aspect-warning-and-explicit-black-padding'
  field.set_input_files(str(ROOT/'src/assets/guitars/yamaha-pacifica-612viifm/01-black.jpg'))
  expect(page.locator('[data-upload-status=needs-layout]')).to_have_count(1);expect(page.get_by_role('button',name='อัปโหลด 1 ภาพที่ตรวจแล้ว',exact=True)).to_be_disabled();assert page.evaluate('__imageFixture.uploads.length')==3
  page.get_by_role('button',name='จัดลงกรอบดำโดยไม่ตัดภาพ',exact=True).click();expect(page.locator('[data-upload-status=ready]')).to_have_count(1)
  dimensions=page.locator('.admin-upload-queue img').evaluate('async i=>{await i.decode();const c=document.createElement("canvas");c.width=i.naturalWidth;c.height=i.naturalHeight;const x=c.getContext("2d");x.drawImage(i,0,0);return {w:i.naturalWidth,h:i.naturalHeight,border:[...x.getImageData(2,600,1,1).data]}}')
  assert dimensions['w']==dimensions['h']==1200 and max(dimensions['border'][:3])<5,dimensions
  passed(current,dimensions)
  current='registration-failure-cleans-only-new-file-and-retry-has-no-duplicates'
  page.evaluate('__imageFixture.failRegistrationOnce=true');page.get_by_role('button',name='อัปโหลด 1 ภาพที่ตรวจแล้ว',exact=True).click()
  expect(page.locator('[data-upload-status=ready]')).to_have_count(1);expect(page.locator('.admin-alert[role=alert]')).to_be_visible();assert page.evaluate('__imageFixture.removed.length')==1
  assert page.evaluate('__imageFixture.row.published.gallery.length')==3
  page.get_by_role('button',name='อัปโหลด 1 ภาพที่ตรวจแล้ว',exact=True).click();expect(page.locator('.admin-upload-queue')).to_have_count(0);expect(page.locator('.admin-images>li')).to_have_count(4)
  page.get_by_role('button',name='บันทึกแบบร่าง',exact=True).click();expect(page.get_by_role('status').filter(has_text='บันทึกแบบร่างแล้ว')).to_be_visible()
  assert page.evaluate('__imageFixture.row.draft.gallery.length')==4 and page.evaluate('__imageFixture.row.published.gallery.length')==3
  page.get_by_role('button',name='เผยแพร่',exact=True).click();expect(page.get_by_role('status').filter(has_text='เผยแพร่แล้ว')).to_be_visible();assert page.evaluate('new Set(__imageFixture.row.published.gallery.map(i=>i.storagePath)).size')==4
  passed(current,{'registrationFailureIsSimulated':True,'onlyFailedNewObjectRemoved':True,'originalsNotRemoved':True,'retryUniqueImages':4})
  current='small-source-not-upscaled-and-removable-after-rights-unchecked'
  field.set_input_files(str(ROOT/'src/assets/home-categories/electric-300.webp'));expect(page.locator('[data-upload-status=needs-layout]')).to_have_count(1)
  page.get_by_role('button',name='จัดลงกรอบดำโดยไม่ตัดภาพ',exact=True).click();expect(page.locator('[data-upload-status=ready]')).to_have_count(1)
  im=page.locator('.admin-upload-queue img');assert im.evaluate('(i)=>i.naturalWidth===800&&i.naturalHeight===800')
  page.get_by_label('ฉันมีสิทธิ์ใช้ภาพเหล่านี้ และภาพตรงกับรุ่นนี้',exact=True).uncheck();page.get_by_role('button',name='นำออกจากรายการอัปโหลด',exact=True).click();expect(page.locator('.admin-upload-queue')).to_have_count(0)
  page.evaluate('__imageFixture.unmount()')
  leftovers=page.evaluate('({remaining:__blobAudit.created.filter(u=>!__blobAudit.revoked.includes(u)),storage:[...__imageFixture.blobs.values()]})')
  assert set(leftovers['remaining'])==set(leftovers['storage']),leftovers
  passed(current,{'smallDeliverySize':[800,800],'noSourceUpscale':True,'localPreviewURLsReleased':True})
 except Exception:
  report['checks'].append({'name':current,'passed':False,'error':traceback.format_exc()});print('FAIL',current,traceback.format_exc(),flush=True)
  page.screenshot(path=str(OUT/'screenshots'/'admin-upload-FAIL.png'),full_page=True,animations='disabled')
 finally:
  report['passed']=all(x['passed'] for x in report['checks']) and not report['errors'];(OUT/'tests/admin-upload-browser.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');b.close()
print(json.dumps({'passed':report['passed'],'checks':len(report['checks']),'errors':report['errors']}));raise SystemExit(not report['passed'])
