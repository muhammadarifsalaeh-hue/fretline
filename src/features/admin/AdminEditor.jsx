import { useEffect,useState } from 'react';
import { SPEC_GROUPS,TYPES,prepareDraft,validateDraft,completeness } from './product';
import { resolveRecord,signedImages } from './publicCatalog';
import { compressImage } from './images';
import { adminError } from './errors';

function Field({label,value,onChange,type='text',...props}){
  return <label>{label}<input type={type} value={value??''} onChange={e=>onChange(e.target.value)} {...props}/></label>;
}
export default function AdminEditor({client,row,brands,onBack,onSaved}){
  const [record,setRecord]=useState(row),[draft,setDraft]=useState(()=>structuredClone(row.draft));
  const [busy,setBusy]=useState(false),[error,setError]=useState(''),[message,setMessage]=useState('');
  const [tab,setTab]=useState('general'),[images,setImages]=useState([]),[registry,setRegistry]=useState([]),[history,setHistory]=useState([]),[prices,setPrices]=useState([]),[rights,setRights]=useState(false);
  const dirty=JSON.stringify(draft)!==JSON.stringify(record.draft);
  useEffect(()=>{
    const warn=e=>{if(dirty){e.preventDefault();e.returnValue='';}};
    const navigate=e=>{const link=e.target.closest?.('a[href]');if(dirty&&link&&link.target!=='_blank'&&!confirm('มีข้อมูลที่ยังไม่บันทึก ต้องการออกจากหน้านี้หรือไม่?')){e.preventDefault();e.stopPropagation();}};
    window.addEventListener('beforeunload',warn);document.addEventListener('click',navigate,true);
    return()=>{window.removeEventListener('beforeunload',warn);document.removeEventListener('click',navigate,true);};
  },[dirty]);
  useEffect(()=>{let live=true;signedImages(client,[draft]).then(map=>{if(live)setImages(resolveRecord(draft,map).gallery);}).catch(()=>{if(live)setError('โหลดตัวอย่างภาพไม่สำเร็จ กรุณาลองเปิดรุ่นนี้ใหม่');});return()=>{live=false;};},[client,draft.gallery]);
  useEffect(()=>{if(!record.id)return;let live=true;(async()=>{
    const [im,logs,pr]=await Promise.all([client.from('guitar_images').select('*').eq('guitar_id',record.id),client.from('audit_logs').select('*').eq('guitar_id',record.id).order('id',{ascending:false}).limit(30),client.from('guitar_prices').select('*').eq('guitar_id',record.id).order('id',{ascending:false}).limit(30)]);
    if(im.error||logs.error||pr.error)throw im.error||logs.error||pr.error;
    if(live){setRegistry(im.data);setHistory(logs.data);setPrices(pr.data);}
  })().catch(()=>{if(live)setError('โหลดประวัติไม่สำเร็จ');});return()=>{live=false;};},[client,record.id,record.revision]);
  function change(key,value){setDraft(d=>({...d,[key]:value}));}
  function spec(key,value){setDraft(d=>({...d,specs:{...d.specs,[key]:value}}));}
  function source(kind,key,value){setDraft(d=>({...d,[kind]:{...d[kind],[key]:value}}));}
  async function save(action='draft'){
    setError('');setMessage('');
    const data=prepareDraft(draft),invalid=validateDraft(data,action==='publish');
    if(invalid){setError(invalid);return;}
    if(action==='publish'&&!confirm('เผยแพร่ข้อมูลรุ่นนี้บนเว็บไซต์?'))return;
    if(action==='hide'&&!confirm('ซ่อนรุ่นนี้จากผู้เข้าชม? ข้อมูลจะยังอยู่ใน Admin'))return;
    setBusy(true);
    try{
      let result=record;
      if(dirty||!record.id){const {data:saved,error:e}=await client.rpc('admin_save_guitar',{p_data:data,p_expected_revision:record.revision??null});if(e)throw e;result=saved;}
      if(action!=='draft'){const {data:saved,error:e}=await client.rpc('admin_set_publication',{p_id:result.id,p_expected_revision:result.revision,p_action:action});if(e)throw e;result=saved;}
      setRecord(result);setDraft(structuredClone(result.draft));onSaved(result);
      setMessage(action==='publish'?'เผยแพร่แล้ว รีเฟรชหน้าเว็บไซต์เพื่อรับข้อมูลล่าสุด':action==='hide'?'ซ่อนสินค้าแล้ว':'บันทึก Draft แล้ว ข้อมูล Published ยังเหมือนเดิม');
    }catch(e){setError(adminError(e));}finally{setBusy(false);}
  }
  async function upload(files){
    if(!record.id||!rights)return;
    if(draft.gallery.length+files.length>30){setError('เก็บได้สูงสุด 30 รูปต่อรุ่น');return;}
    setBusy(true);setError('');setMessage('กำลังย่อและอัปโหลดภาพ');
    try{
      for(const file of files){
        const {blob,width,height,extension}=await compressImage(file);
        const path=`${record.id}/${crypto.randomUUID()}.${extension}`;
        const {error:up}=await client.storage.from('guitar-images').upload(path,blob,{contentType:blob.type,upsert:false});if(up)throw up;
        const metadata={rightsConfirmed:true,width,height,label:file.name.replace(/\.[^.]+$/,''),originalName:file.name};
        const {data:image,error:reg}=await client.rpc('admin_register_image',{p_id:record.id,p_path:path,p_metadata:metadata});
        if(reg){await client.storage.from('guitar-images').remove([path]);throw reg;}
        setRegistry(list=>[...list,image]);
        setDraft(d=>({...d,gallery:[...d.gallery,{id:image.id,storagePath:path,...metadata}]}));
      }
      setMessage('อัปโหลดแล้ว กรุณาบันทึก Draft หรือ Publish เพื่อใช้ภาพ');
    }catch(e){setError(e.message?.includes('รองรับ')||e.message?.includes('ภาพต้อง')||e.message?.includes('ย่อภาพ')?e.message:adminError(e));setMessage('ภาพที่อัปโหลดสำเร็จยังอยู่ในร่าง');}
    finally{setBusy(false);}
  }
  function reorder(index,to){setDraft(d=>{const gallery=[...d.gallery];const [item]=gallery.splice(index,1);gallery.splice(to,0,item);return {...d,gallery};});}
  async function purge(path){
    if(!confirm('ลบไฟล์ภาพที่ไม่ใช้งานนี้ถาวร?'))return;
    setBusy(true);setError('');
    try{const {error:e}=await client.rpc('admin_forget_image',{p_path:path});if(e)throw e;const {error:removed}=await client.storage.from('guitar-images').remove([path]);if(removed)throw removed;setRegistry(list=>list.filter(im=>im.storage_path!==path));setMessage('ลบภาพที่ไม่ใช้งานแล้ว');}catch(e){setError(adminError(e));}finally{setBusy(false);}
  }
  const refs=new Set([...draft.gallery,...(record.published?.gallery??[])].map(im=>im.storagePath).filter(Boolean));
  const unused=registry.filter(im=>!refs.has(im.storage_path));
  return <div className="admin-editor">
    <div className="admin-actions admin-toolbar"><button disabled={busy} onClick={()=>{if(!dirty||confirm('มีข้อมูลที่ยังไม่บันทึก ต้องการกลับหรือไม่?'))onBack();}}>← กลับรายการ</button><span className="admin-muted">{record.status??'draft'} · {dirty?'ยังไม่บันทึก':'บันทึกแล้ว'}{record.revision?` · v${record.revision}`:''}</span></div>
    <h2 className="admin-editor-title">{record.id?draft.name||draft.id:'เพิ่มกีตาร์'}</h2>
    {error&&<p className="admin-alert" role="alert">{error}</p>}{message&&<p className="admin-notice" role="status">{message}</p>}
    <div className="admin-tabs" aria-label="ส่วนจัดการสินค้า">{[['general','รายละเอียด'],['images','รูปภาพ'],['price','ราคา'],['specs','สเปก'],['history','ประวัติ']].map(([id,label])=><button key={id} aria-pressed={tab===id} onClick={()=>setTab(id)}>{label}</button>)}</div>
    <fieldset className="admin-panel" disabled={busy}>
      {tab==='general'&&<><div className="admin-fields"><Field label="ID สินค้า" value={draft.id} onChange={v=>change('id',v)} readOnly={Boolean(record.id)} autoCapitalize="none" spellCheck={false}/><Field label="ชื่อรุ่น" value={draft.name} onChange={v=>change('name',v)} maxLength={250}/><label>แบรนด์<select value={draft.brand} onChange={e=>change('brand',e.target.value)}>{brands.map(b=><option key={b.id}>{b.name}</option>)}</select></label><label>ประเภทกีตาร์<select value={draft.category} onChange={e=>change('category',e.target.value)}>{TYPES.map(([id,n])=><option key={id} value={id}>{n}</option>)}</select></label></div><label>คำอธิบายภาษาไทย<textarea value={draft.description??''} onChange={e=>change('description',e.target.value)} rows={5}/></label><label>คำอธิบายภาษาอังกฤษ<textarea value={draft.descriptionEn??''} onChange={e=>change('descriptionEn',e.target.value)} rows={5}/></label><label className="admin-checkbox"><input type="checkbox" checked={Boolean(draft.featured)} onChange={e=>change('featured',e.target.checked)}/>แนะนำในรายการยอดนิยม</label></>}
      {tab==='images'&&<><h3>รูปภาพสินค้า</h3><p className="admin-muted">รูปแรกเป็นรูปปก ย้ายลำดับด้วยปุ่ม ไม่ต้องลาก รูปเดิมจะไม่ถูกลบอัตโนมัติ</p>{!record.id&&<p className="admin-notice">บันทึก Draft ครั้งแรกก่อนอัปโหลดภาพ</p>}<label className="admin-checkbox"><input type="checkbox" checked={rights} onChange={e=>setRights(e.target.checked)}/>ฉันมีสิทธิ์ใช้ภาพเหล่านี้ และภาพตรงกับรุ่นนี้</label><label>เลือกภาพจาก Photos หรือ Files<input type="file" accept="image/jpeg,image/png,image/webp" multiple disabled={!record.id||!rights} onChange={e=>{const files=[...e.target.files];e.target.value='';upload(files);}}/></label>
        <ul className="admin-images">{draft.gallery.map((im,index)=><li key={im.id??im.storagePath??im.legacyIndex}>{images[index]?.src?<img src={images[index].src} alt={im.label||'ภาพสินค้า'}/>:<p>กำลังโหลดภาพ</p>}<p>{index===0?'รูปปก':`ภาพที่ ${index+1}`}</p><div className="admin-actions"><button disabled={index===0} onClick={()=>reorder(index,0)}>ตั้งเป็นรูปปก</button><button disabled={index===0} aria-label={`ย้ายภาพ ${index+1} ขึ้น`} onClick={()=>reorder(index,index-1)}>↑</button><button disabled={index===draft.gallery.length-1} aria-label={`ย้ายภาพ ${index+1} ลง`} onClick={()=>reorder(index,index+1)}>↓</button><button onClick={()=>{if(confirm('นำภาพนี้ออกจาก Draft? จะยังไม่เปลี่ยนรูป Published จนกดเผยแพร่'))change('gallery',draft.gallery.filter((_,i)=>i!==index));}}>นำออกจากร่าง</button></div></li>)}</ul>
        {unused.length>0&&<details><summary>ไฟล์อัปโหลดที่ไม่ใช้งาน ({unused.length})</summary>{unused.map(im=><div className="admin-actions" key={im.id}><span>{im.metadata.label}</span><button onClick={()=>purge(im.storage_path)}>ลบไฟล์ถาวร</button></div>)}<p className="admin-muted">ต้องนำภาพออกจาก Draft ที่บันทึกแล้ว และจาก Published ก่อน จึงจะลบไฟล์ได้</p></details>}</>}
      {tab==='price'&&<><h3>ราคาเงินบาท</h3><div className="admin-fields"><Field label="ราคา (THB) — เว้นว่างเมื่อไม่ทราบ" type="number" min="0.01" step="0.01" value={draft.price} onChange={v=>change('price',v)}/><Field label="แหล่งอ้างอิงราคา (URL)" type="url" value={draft.priceSource?.url} onChange={v=>source('priceSource','url',v)}/><Field label="วันที่ตรวจสอบราคา" type="date" value={draft.priceSource?.verifiedOn} onChange={v=>source('priceSource','verifiedOn',v)}/><label>ประเภทราคา<select value={draft.priceSource?.kind??'retailer-listed'} onChange={e=>source('priceSource','kind',e.target.value)}><option value="retailer-listed">ราคาที่ร้านแสดง</option><option value="manufacturer-recommended-retail">ราคาแนะนำจากผู้ผลิต</option></select></label><Field label="ชื่อแหล่งอ้างอิง" value={draft.priceSource?.note} onChange={v=>source('priceSource','note',v)}/></div><p className="admin-muted">ไม่มีราคายืนยันจะแสดง “สอบถามราคา” ไม่ใช้ 0 บาทแทน</p></>}
      {tab==='specs'&&<><p className="admin-muted">เว้นว่างเมื่อไม่มีข้อมูล ห้ามเติมโดยคาดเดา · ยังขาดสเปกหลัก {completeness(draft).length} ช่อง</p>{SPEC_GROUPS.map(([title,fields])=><section className="admin-spec-group" key={title}><h3>{title}</h3><div className="admin-fields">{fields.map(([key,label,type])=><Field key={key} label={label} type={type??'text'} step={type==='number'?'any':undefined} value={draft.specs[key]} onChange={v=>spec(key,v)}/>)}</div></section>)}<h3>หลักฐานสเปก</h3><div className="admin-fields"><Field label="แหล่งสเปก (URL)" type="url" value={draft.source?.url} onChange={v=>source('source','url',v)}/><Field label="วันที่ตรวจสอบสเปก" type="date" value={draft.source?.verifiedOn} onChange={v=>source('source','verifiedOn',v)}/><Field label="ชื่อแหล่งข้อมูล" value={draft.source?.note} onChange={v=>source('source','note',v)}/></div></>}
      {tab==='history'&&<><h3>ประวัติราคา</h3><ul className="admin-history">{prices.map(p=><li key={p.id}>{p.amount==null?'สอบถามราคา':`฿${Number(p.amount).toLocaleString('th-TH')}`} · {p.checked_on??'—'}<br/>{p.source?.url&&<a href={p.source.url} target="_blank" rel="noopener noreferrer">แหล่งราคา</a>}</li>)}</ul><h3>การแก้ไขล่าสุด</h3><ul className="admin-history">{history.map(log=><li key={log.id}>{log.action} · {new Date(log.created_at).toLocaleString('th-TH')}</li>)}</ul>{record.published&&<button onClick={()=>{if(confirm('คืน Draft ให้เหมือน Published ล่าสุด? กรุณาบันทึกอีกครั้งเพื่อยืนยัน'))setDraft(structuredClone(record.published));}}>คืนร่างจาก Published ล่าสุด</button>}</>}
    </fieldset>
    <div className="admin-save-bar"><button disabled={busy} onClick={()=>save('draft')}>{busy?'กำลังบันทึก…':'บันทึก Draft'}</button><button className="admin-primary" disabled={busy} onClick={()=>save('publish')}>Publish</button>{record.id&&<button className="admin-danger" disabled={busy||record.status==='hidden'} onClick={()=>save('hide')}>ซ่อนสินค้า</button>}{record.published&&<a href={`/guitars/${record.id}?fretline-preview=1`} target="_blank" rel="noopener noreferrer">ดูหน้า Published ↗</a>}</div>
  </div>;
}
