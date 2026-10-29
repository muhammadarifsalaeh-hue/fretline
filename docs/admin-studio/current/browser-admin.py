"""Browser acceptance against REAL local PostgREST/PostgreSQL.
Auth and Storage HTTP are contract fixtures, NOT hosted Supabase verification.
Run with production preview on 4179 and isolated QA API on 55433.
"""
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request,urlopen
from urllib.error import HTTPError
from playwright.sync_api import sync_playwright,expect
from PIL import Image
import base64,hashlib,hmac,json,time,subprocess,traceback,io

OUT=Path(__file__).resolve().parent
BASE='http://127.0.0.1:4179'
SECRET=b'fretline-local-fixture-jwt-not-a-production-secret'
OWNER='11111111-1111-1111-1111-111111111111'
VISITOR='22222222-2222-2222-2222-222222222222'
def sql(query):
    r=subprocess.run(['docker','exec','-i','fretline-admin-pg','psql','-U','postgres','-At','-v','ON_ERROR_STOP=1'],input=query,text=True,capture_output=True)
    if r.returncode: raise RuntimeError(r.stderr)
    return r.stdout.strip()
sql(f"insert into auth.users(id,email) values('{OWNER}','owner@example.test'),('{VISITOR}','visitor@example.test') on conflict do nothing; insert into public.admin_users(user_id) values('{OWNER}') on conflict do nothing;")
sql("delete from public.audit_logs where guitar_id like 'qa-browser-%'; delete from public.guitar_prices where guitar_id like 'qa-browser-%'; delete from public.guitar_specifications where guitar_id like 'qa-browser-%'; delete from public.guitar_images where guitar_id like 'qa-browser-%'; delete from storage.objects where name like 'qa-browser-%'; delete from public.guitars where id like 'qa-browser-%';")
def jwt(uid):
    enc=lambda v:base64.urlsafe_b64encode(json.dumps(v,separators=(',',':')).encode()).rstrip(b'=')
    content=enc({'alg':'HS256','typ':'JWT'})+b'.'+enc({'sub':uid,'role':'authenticated','aud':'authenticated','exp':int(time.time())+7200})
    return (content+b'.'+base64.urlsafe_b64encode(hmac.new(SECRET,content,hashlib.sha256).digest()).rstrip(b'=')).decode()
report={'scope':'actual browser + local real PostgreSQL/PostgREST; Auth/Storage HTTP use fixtures','hostedSupabaseTested':False,'physicalIPadTested':False,'checks':[],'errors':[],'uploads':[],'screenshots':[]}
blobs={}
captured_uploads={}
def bridge(route):
    req=route.request; path=urlparse(req.url).path
    if req.method=='OPTIONS':route.fulfill(status=204,headers={'access-control-allow-origin':'*','access-control-allow-headers':'*','access-control-allow-methods':'*'});return
    def answer(data,status=200):route.fulfill(status=status,content_type='application/json',headers={'access-control-allow-origin':'*'},body=json.dumps(data))
    if '/auth/v1/token' in path:
        d=json.loads(req.post_data); uid=VISITOR if d.get('email')=='visitor@example.test' else OWNER
        answer({'access_token':jwt(uid),'refresh_token':'local-fixture-refresh','token_type':'bearer','expires_in':7200,'expires_at':int(time.time())+7200,'user':{'id':uid,'email':d['email'],'role':'authenticated','aud':'authenticated','created_at':'2026-10-29T00:00:00Z'}});return
    if '/auth/v1/logout' in path:answer({});return
    if '/rest/v1/' in path:
        headers={k:v for k,v in req.headers.items() if k.lower() in ['authorization','prefer','range','content-type','accept','accept-profile','content-profile']}
        if headers.get('authorization','').endswith('sb_publishable_fixture'):headers.pop('authorization')
        target='http://127.0.0.1:55433'+req.url.split('/rest/v1',1)[1]
        request=Request(target,data=req.post_data_buffer,method=req.method,headers=headers)
        try:
            with urlopen(request,timeout=20) as r:body=r.read();status=r.status;content=r.headers.get('Content-Type','application/json')
        except HTTPError as e:body=e.read();status=e.code;content='application/json'
        route.fulfill(status=status,body=body,content_type=content,headers={'access-control-allow-origin':'*'});return
    if path=='/storage/v1/object/sign/guitar-images':
        answer([{'path':p,'error':None,'signedURL':'/object/sign/guitar-images/'+p+'?token=local-fixture'} for p in json.loads(req.post_data)['paths']]);return
    if path.startswith('/storage/v1/object/sign/guitar-images/'):
        key=path.split('/guitar-images/',1)[1]
        route.fulfill(status=200,body=blobs[key],content_type='image/webp',headers={'access-control-allow-origin':'*'});return
    if path.startswith('/storage/v1/object/guitar-images/') and req.method in ['POST','PUT']:
        key=path.split('/guitar-images/',1)[1];assert "'" not in key
        # Storage-js wraps a Blob in multipart FormData; parse the file part.
        raw=req.post_data_buffer
        from email.parser import BytesParser
        from email.policy import default
        msg=BytesParser(policy=default).parsebytes(('Content-Type: '+req.headers['content-type']+'\r\nMIME-Version: 1.0\r\n\r\n').encode()+raw)
        data=next((part.get_payload(decode=True) for part in msg.iter_parts() if part.get_content_type().startswith('image/')),raw) if msg.is_multipart() else raw
        # WebKit's interception protocol omits file bytes from multipart bodies.
        # Instrument fetch in the test page to retain the ACTUAL compressed Blob;
        # never substitute an invented image or change the production uploader.
        if not data and req.url in captured_uploads:data=bytes(captured_uploads[req.url])
        im=Image.open(io.BytesIO(data))
        assert max(im.size)<=1800
        blobs[key]=data;report['uploads'].append({'path':key,'size':len(data),'dimensions':im.size,'format':im.format})
        sql(f"insert into storage.objects(bucket_id,name) values('guitar-images','{key}');")
        answer({'Key':'guitar-images/'+key,'Id':'33333333-3333-3333-3333-333333333333'});return
    if path=='/storage/v1/object/guitar-images' and req.method=='DELETE':
        for key in json.loads(req.post_data)['prefixes']:
            assert "'" not in key
            sql(f"delete from storage.objects where bucket_id='guitar-images' and name='{key}';")
            blobs.pop(key,None)
        answer([]);return
    raise RuntimeError(f'Unexpected contract request: {req.method} {path}')

with sync_playwright() as p:
  for engine in ['chromium','webkit']:
    b=p.chromium.launch(executable_path='/usr/bin/chromium',args=['--no-sandbox','--enable-unsafe-swiftshader']) if engine=='chromium' else p.webkit.launch()
    context=b.new_context(viewport={'width':1194,'height':834},has_touch=True,reduced_motion='reduce')
    context.expose_function('qaCaptureImage',lambda url,data:captured_uploads.update({url:data}))
    context.add_init_script("""const originalFetch=window.fetch.bind(window);window.fetch=async(input,init)=>{
      const url=typeof input==='string'?input:input.url;
      if(url.includes('/storage/v1/object/guitar-images/') && init?.body instanceof FormData){
        const blob=[...init.body.values()].find(v=>v instanceof Blob);
        if(blob)await window.qaCaptureImage(url,Array.from(new Uint8Array(await blob.arrayBuffer())));
      }
      return originalFetch(input,init);
    };""")
    context.route('https://qa.supabase.co/**',bridge)
    page=context.new_page();page.on('dialog',lambda d:d.accept());page.on('pageerror',lambda e:report['errors'].append(str(e)))
    gid='qa-browser-'+engine
    try:
      page.goto(BASE+'/admin',wait_until='networkidle')
      page.get_by_label('Project URL',exact=True).fill('https://qa.supabase.co')
      page.get_by_label('Publishable key',exact=True).fill('sb_publishable_fixture')
      page.get_by_role('button',name='บันทึกการเชื่อมต่อบนเครื่องนี้',exact=True).click()
      expect(page.get_by_role('heading',name='เข้าสู่ระบบผู้ดูแล')).to_be_visible()
      def login(email):
        page.get_by_label('อีเมล',exact=True).fill(email);page.get_by_label('รหัสผ่าน',exact=True).fill('local-fixture-password')
        page.get_by_role('button',name='เข้าสู่ระบบ',exact=True).click()
      login('visitor@example.test')
      expect(page.get_by_role('heading',name='บัญชีนี้ไม่มีสิทธิ์แอดมิน')).to_be_visible()
      expect(page.get_by_role('button',name='+ เพิ่มกีตาร์',exact=True)).to_have_count(0)
      page.get_by_role('button',name='ออกจากระบบ',exact=True).click()
      login('owner@example.test')
      expect(page.get_by_role('button',name='+ เพิ่มกีตาร์',exact=True)).to_be_visible(timeout=20000)
      report['checks'].append({'name':engine+'-login-logout-and-nonadmin-guard','passed':True})
      page.get_by_role('button',name='+ เพิ่มกีตาร์',exact=True).click()
      page.get_by_label('ID สินค้า',exact=True).fill(gid);page.get_by_label('ชื่อรุ่น',exact=True).fill('QA Guitar '+engine)
      page.get_by_role('button',name='บันทึก Draft',exact=True).click()
      expect(page.get_by_role('button',name='ซ่อนสินค้า',exact=True)).to_be_visible()
      assert sql(f"select published is null from public.guitars where id='{gid}';")=='t'
      page.get_by_role('button',name='ราคา',exact=True).click()
      page.get_by_label('ราคา (THB) — เว้นว่างเมื่อไม่ทราบ',exact=True).fill('12345')
      page.get_by_label('แหล่งอ้างอิงราคา (URL)',exact=True).fill('https://example.test/qa-price')
      page.get_by_label('วันที่ตรวจสอบราคา',exact=True).fill('2026-10-29')
      page.get_by_role('button',name='สเปก',exact=True).click()
      page.get_by_label('ทรงบอดี้',exact=True).fill('QA Shape');page.get_by_label('จำนวนสาย',exact=True).fill('6')
      page.get_by_label('แหล่งสเปก (URL)',exact=True).fill('https://example.test/qa-spec')
      page.get_by_label('วันที่ตรวจสอบสเปก',exact=True).fill('2026-10-29')
      page.get_by_role('button',name='รูปภาพ',exact=True).click()
      page.get_by_label('ฉันมีสิทธิ์ใช้ภาพเหล่านี้ และภาพตรงกับรุ่นนี้',exact=True).check()
      image=io.BytesIO();Image.new('RGB',(2400,1600),'#ab7b31').save(image,'PNG')
      page.locator('input[type=file]').set_input_files([{'name':'qa-one.png','mimeType':'image/png','buffer':image.getvalue()},{'name':'qa-two.png','mimeType':'image/png','buffer':image.getvalue()}])
      expect(page.locator('.admin-images li')).to_have_count(2,timeout=30000)
      expect(page.get_by_role('button',name='Publish',exact=True)).to_be_enabled()
      page.locator('.admin-images li').nth(1).get_by_role('button',name='ตั้งเป็นรูปปก',exact=True).click()
      page.get_by_role('button',name='Publish',exact=True).click()
      expect(page.get_by_role('status').filter(has_text='เผยแพร่แล้ว')).to_be_visible(timeout=15000)
      assert sql(f"select published->>'price' from public.guitars where id='{gid}';")=='12345'
      report['checks'].append({'name':engine+'-draft-price-spec-two-images-cover-publish-real-sql','passed':True})
      for name,size in [('desktop',(1440,1000)),('landscape',(1194,834)),('portrait',(768,1024)),('mobile',(390,844))]:
        page.set_viewport_size({'width':size[0],'height':size[1]})
        assert page.evaluate('document.documentElement.scrollWidth<=innerWidth+1')
        page.locator('.admin-editor-title').scroll_into_view_if_needed()
        filename=f'{engine}-admin-images-{name}.png';page.screenshot(path=str(OUT/filename),animations='disabled');report['screenshots'].append(filename)
      report['checks'].append({'name':engine+'-four-responsive-sizes','passed':True})
      # Published catalog hydration must happen before module-level indexes load.
      page.goto(BASE+'/guitars?fretline-preview=1&q='+gid,wait_until='networkidle')
      expect(page.locator('[data-guitar-id="'+gid+'"]')).to_contain_text('฿12,345')
      page.goto(BASE+'/guitars/'+gid+'?fretline-preview=1',wait_until='networkidle')
      expect(page.locator('main h1')).to_contain_text('QA Guitar')
      expect(page.locator('.gallery-thumbnails li')).to_have_count(2)
      page.goto(BASE+'/compare?fretline-preview=1&ids='+gid+',yamaha-pacifica-612viifm',wait_until='networkidle')
      expect(page.locator('[data-compare-row="price"]')).to_contain_text('฿12,345')
      expect(page.locator('[data-compare-row="bodyShape"]')).to_contain_text('QA Shape')
      report['checks'].append({'name':engine+'-published-refresh-catalog-detail-compare-new-id','passed':True})
      page.goto(BASE+'/admin',wait_until='networkidle')
      page.get_by_role('searchbox',name='ค้นหา',exact=True).fill(gid)
      page.get_by_role('button',name='แก้ไข QA Guitar '+engine,exact=True).click()
      page.get_by_role('button',name='รูปภาพ',exact=True).click()
      page.locator('.admin-images li').nth(1).get_by_role('button',name='นำออกจากร่าง',exact=True).click()
      page.get_by_role('button',name='บันทึก Draft',exact=True).click()
      expect(page.get_by_role('status').filter(has_text='บันทึก Draft แล้ว')).to_be_visible()
      assert sql(f"select jsonb_array_length(published->'gallery') from public.guitars where id='{gid}';")=='2'
      page.get_by_role('button',name='Publish',exact=True).click()
      expect(page.get_by_role('status').filter(has_text='เผยแพร่แล้ว')).to_be_visible()
      page.get_by_text('ไฟล์อัปโหลดที่ไม่ใช้งาน (1)',exact=True).click()
      page.get_by_role('button',name='ลบไฟล์ถาวร',exact=True).click()
      expect(page.get_by_role('status').filter(has_text='ลบภาพที่ไม่ใช้งานแล้ว')).to_be_visible()
      assert sql(f"select count(*) from public.guitar_images where guitar_id='{gid}';")=='1'
      report['checks'].append({'name':engine+'-remove-draft-image-keeps-published-then-purge-unused','passed':True})
      page.get_by_role('button',name='รายละเอียด',exact=True).click()
      page.get_by_label('ชื่อรุ่น',exact=True).fill('Draft never public')
      page.get_by_role('button',name='บันทึก Draft',exact=True).click()
      expect(page.get_by_role('status').filter(has_text='บันทึก Draft แล้ว')).to_be_visible()
      assert sql(f"select published->>'name' from public.guitars where id='{gid}';")=='QA Guitar '+engine
      page.get_by_role('button',name='ซ่อนสินค้า',exact=True).click()
      expect(page.get_by_role('status').filter(has_text='ซ่อนสินค้าแล้ว')).to_be_visible()
      page.goto(BASE+'/guitars?fretline-preview=1&q='+gid,wait_until='networkidle')
      expect(page.locator('[data-guitar-id="'+gid+'"]')).to_have_count(0)
      report['checks'].append({'name':engine+'-draft-isolation-and-hide-public','passed':True})
      print('PASS',engine,'complete local-API workflow',flush=True)
    except Exception:
      error=traceback.format_exc();report['checks'].append({'name':engine+'-workflow','passed':False,'error':error});print(error,flush=True)
      try:page.screenshot(path=str(OUT/(engine+'-FAIL.png')))
      except:pass
    finally:context.close();b.close()
report['passed']=all(c['passed'] for c in report['checks']) and len(report['checks'])==12 and not report['errors']
(OUT/'browser-results.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print('FINAL',report['passed'],len(report['checks']),report['errors'],flush=True)
raise SystemExit(0 if report['passed'] else 1)
