import { useEffect, useState } from 'react';
import { getSupabase, readConnection, saveConnection, validateConnection } from '@/features/admin/config';
import { blankGuitar, completeness, TYPES } from '@/features/admin/product';
import { publicationLabel } from '@/features/admin/displayLabels';
import AdminEditor from '@/features/admin/AdminEditor';
import AdminSetup from '@/features/admin/AdminSetup';
import { adminError } from '@/features/admin/errors';
import '@/styles/admin-studio.css';

export default function AdminStudioPage() {
  const [connection]=useState(readConnection);
  const [client,setClient]=useState(null), [session,setSession]=useState(null), [access,setAccess]=useState(null);
  const [rows,setRows]=useState([]), [brands,setBrands]=useState([]), [selected,setSelected]=useState(null);
  const [busy,setBusy]=useState(false), [error,setError]=useState(''), [message,setMessage]=useState('');
  const [email,setEmail]=useState(''), [password,setPassword]=useState('');
  const [query,setQuery]=useState(''), [brand,setBrand]=useState(''), [type,setType]=useState(''), [status,setStatus]=useState(''), [page,setPage]=useState(1);
  const [recovery,setRecovery]=useState(()=>new URLSearchParams(location.search).get('recovery')==='1'), [retry,setRetry]=useState(0);
  useEffect(()=>{document.title='จัดการเว็บไซต์ — Fretline';},[]);
  useEffect(()=>{
    if(!connection) return undefined;
    let alive=true, subscription;
    getSupabase().then(c=>{
      if(!alive)return;
      setClient(c);
      c.auth.getSession().then(({data,error:e})=>{if(alive){if(e)setError(adminError(e));setSession(data.session);}});
      subscription=c.auth.onAuthStateChange((event,next)=>{if(alive){setSession(next);if(event==='PASSWORD_RECOVERY')setRecovery(true);}}).data.subscription;
    }).catch(e=>{if(alive)setError(adminError(e));});
    return()=>{alive=false;subscription?.unsubscribe();};
  },[connection]);
  useEffect(()=>{
    let alive=true; setRows([]);setSelected(null);setAccess(null);
    if(!session || !client)return undefined;
    (async()=>{
      const {data:allowed,error:e}=await client.rpc('fretline_is_admin');
      if(e)throw e;
      if(!alive)return;
      if(!allowed){setAccess(false);return;}
      const [g,b]=await Promise.all([client.from('guitars').select('*').order('position').order('id'),client.from('brands').select('*').order('name')]);
      if(g.error||b.error)throw g.error||b.error;
      if(alive){setRows(g.data);setBrands(b.data);setAccess(true);setError('');}
    })().catch(e=>{if(alive)setError(adminError(e));});
    return()=>{alive=false;};
  },[client,session?.user?.id,retry]);
  async function login(event){
    event.preventDefault();setBusy(true);setError('');setMessage('');
    try{const {error:e}=await client.auth.signInWithPassword({email,password});if(e)throw e;setPassword('');}
    catch(e){setError(adminError(e));}finally{setBusy(false);}
  }
  async function logout(){
    setBusy(true);const {error:e}=await client.auth.signOut();setBusy(false);
    if(e)setError(adminError(e));else{setSession(null);setAccess(null);setSelected(null);setPassword('');setMessage('ออกจากระบบแล้ว');}
  }
  async function recover(){
    if(!email){setError('กรอกอีเมลก่อนขอลิงก์เปลี่ยนรหัสผ่าน');return;}
    setBusy(true);const {error:e}=await client.auth.resetPasswordForEmail(email,{redirectTo:`${location.origin}/admin?recovery=1`});setBusy(false);
    if(e)setError(adminError(e));else setMessage('หากอีเมลนี้มีบัญชี ระบบจะส่งลิงก์เปลี่ยนรหัสผ่านให้');
  }
  async function resetPassword(event){
    event.preventDefault();if(password.length<12){setError('ใช้รหัสผ่านอย่างน้อย 12 ตัวอักษร');return;}
    setBusy(true);const {error:e}=await client.auth.updateUser({password});setBusy(false);
    if(e)setError(adminError(e));else{setPassword('');setRecovery(false);history.replaceState(null,'',location.pathname);setMessage('เปลี่ยนรหัสผ่านแล้ว');}
  }
  const displayed=rows.filter(row=>{
    const d=row.draft;
    return (!query || `${d.id} ${d.brand} ${d.name}`.toLocaleLowerCase().includes(query.toLocaleLowerCase())) && (!brand||d.brand===brand) && (!type||d.category===type)
      && (!status||status===row.status||(status==='missing'&&(completeness(d).length || !d.gallery.length || d.price==null)));
  });
  const safePage=Math.min(page,Math.max(1,Math.ceil(displayed.length/20)));
  const updateFilter=(setter)=>(e)=>{setter(e.target.value);setPage(1);};
  const counts=[['กีตาร์ทั้งหมด',rows.length],['แบรนด์',brands.length],['มีรูป',rows.filter(r=>r.draft.gallery.length).length],['มีราคา',rows.filter(r=>r.draft.price>0).length],['สเปกครบ',rows.filter(r=>!completeness(r.draft).length).length],['ยังขาดข้อมูล',rows.filter(r=>completeness(r.draft).length||!r.draft.gallery.length||r.draft.price==null).length],['แบบร่าง',rows.filter(r=>r.status==='draft').length],['เผยแพร่แล้ว',rows.filter(r=>r.status==='published').length]];
  return <section className="admin-studio container-x" aria-labelledby="admin-title">
    <header className="admin-header"><div><p className="admin-eyebrow">FRETLINE / พื้นที่ผู้ดูแล</p><h1 id="admin-title">จัดการเว็บไซต์</h1></div>
      {session&&<div className="admin-actions"><span className="admin-muted">{session.user.email}</span><button onClick={logout} disabled={busy}>ออกจากระบบ</button></div>}</header>
    {error&&<p role="alert" className="admin-alert">{error}</p>}{message&&<p role="status" className="admin-notice">{message}</p>}
    {!connection?<ConnectionForm/>:recovery?<form onSubmit={resetPassword} className="admin-panel admin-login"><h2>ตั้งรหัสผ่านใหม่</h2><label>รหัสผ่านใหม่<input type="password" autoComplete="new-password" minLength={12} value={password} onChange={e=>setPassword(e.target.value)} required/></label><button className="admin-primary" disabled={busy}>บันทึกรหัสผ่าน</button></form>
      :!session?<form className="admin-panel admin-login" onSubmit={login}><h2>เข้าสู่ระบบผู้ดูแล</h2><label>อีเมล<input type="email" autoComplete="username" value={email} onChange={e=>setEmail(e.target.value)} required/></label><label>รหัสผ่าน<input type="password" autoComplete="current-password" value={password} onChange={e=>setPassword(e.target.value)} required/></label><button className="admin-primary" disabled={busy||!client}>เข้าสู่ระบบ</button><button type="button" onClick={recover} disabled={busy||!client}>ลืมรหัสผ่าน</button><p className="admin-muted">ใช้บัญชีที่เจ้าของโปรเจกต์อนุญาตเท่านั้น</p></form>
        :access===false?<div className="admin-panel"><h2>บัญชีนี้ไม่มีสิทธิ์แอดมิน</h2><p>ให้เจ้าของโปรเจกต์กำหนดสิทธิ์ใน Supabase ก่อน</p><button onClick={()=>setRetry(x=>x+1)}>ตรวจสิทธิ์อีกครั้ง</button></div>
          :access===null?<div className="admin-panel" role="status"><p>กำลังตรวจสิทธิ์ผู้ดูแล</p>{error&&<button onClick={()=>setRetry(x=>x+1)}>ลองอีกครั้ง</button>}</div>
            :selected?<AdminEditor key={selected.id??'new'} client={client} row={selected} brands={brands} onBack={()=>setSelected(null)} onSaved={r=>{setRows(prev=>prev.some(x=>x.id===r.id)?prev.map(x=>x.id===r.id?r:x):[...prev,r]);setSelected(r);}}/>
              :<><div className="admin-stats">{counts.map(([label,n])=><div key={label}><strong>{n}</strong><span>{label}</span></div>)}</div>
                <div className="admin-actions admin-toolbar"><button className="admin-primary" onClick={()=>setSelected({draft:blankGuitar(brands[0]?.name)})}>+ เพิ่มกีตาร์</button><button onClick={()=>setRetry(x=>x+1)}>รีเฟรชข้อมูล</button><a href="/?fretline-preview=1" target="_blank" rel="noopener noreferrer">ดูข้อมูลที่เผยแพร่</a></div>
                <div className="admin-filters"><label>ค้นหา<input type="search" value={query} onChange={updateFilter(setQuery)} placeholder="ชื่อรุ่นหรือ ID"/></label><label>แบรนด์<select value={brand} onChange={updateFilter(setBrand)}><option value="">ทุกแบรนด์</option>{brands.map(b=><option key={b.id}>{b.name}</option>)}</select></label><label>ประเภท<select value={type} onChange={updateFilter(setType)}><option value="">ทุกประเภท</option>{TYPES.map(([id,n])=><option key={id} value={id}>{n}</option>)}</select></label><label>สถานะ<select value={status} onChange={updateFilter(setStatus)}><option value="">ทุกสถานะ</option><option value="draft">แบบร่าง</option><option value="published">เผยแพร่แล้ว</option><option value="hidden">ซ่อน</option><option value="missing">ยังขาดข้อมูล</option></select></label></div>
                <p className="admin-muted" role="status">{displayed.length} รุ่น · หน้า {safePage} / {Math.max(1,Math.ceil(displayed.length/20))}</p>
                <ul className="admin-products">{displayed.slice((safePage-1)*20,safePage*20).map(r=><li key={r.id}><div><span className="admin-eyebrow">{r.draft.brand}</span><h2>{r.draft.name||r.id}</h2><p className="admin-muted">{publicationLabel(r.status)} · {r.draft.price?`฿${r.draft.price.toLocaleString('th-TH')}`:'สอบถามราคา'} · {r.draft.gallery.length} รูป</p></div><button onClick={()=>setSelected(r)} aria-label={`แก้ไข ${r.draft.name||r.id}`}>แก้ไข</button></li>)}</ul>
                {!displayed.length&&<p className="admin-panel">ไม่พบสินค้า</p>}<div className="admin-actions"><button disabled={safePage===1} onClick={()=>setPage(safePage-1)}>ก่อนหน้า</button><button disabled={safePage*20>=displayed.length} onClick={()=>setPage(safePage+1)}>ถัดไป</button></div></>}
    <details className="admin-help"><summary>ตั้งค่า Supabase และเปิดใช้บนเว็บไซต์</summary><AdminSetup connection={connection}/></details>
    <p className="admin-muted admin-footnote">{connection?.deployed?'การเชื่อมต่อมาจากการตั้งค่าเว็บไซต์':'การเชื่อมต่อบนเครื่องนี้เท่านั้น การเปิดใช้กับผู้เข้าชมทุกคนต้องตั้งค่าเว็บไซต์ก่อน'}</p>
  </section>;
}
function ConnectionForm(){
  const [url,setUrl]=useState(''),[key,setKey]=useState(''),[error,setError]=useState('');
  return <form className="admin-panel admin-login" onSubmit={e=>{e.preventDefault();const err=validateConnection(url.trim(),key.trim());if(err){setError(err);return;}try{saveConnection(url,key);location.reload();}catch{setError('บันทึกไม่ได้ กรุณาอนุญาตพื้นที่เก็บข้อมูลของ Safari');}}}><h2>เชื่อมต่อโปรเจกต์ Fretline</h2><p className="admin-muted">กรอกเฉพาะค่าที่ใช้ในหน้าเว็บได้ ไม่ต้องส่งรหัสผ่านหรือคีย์ลับในแชท</p><label>URL โปรเจกต์<input type="url" value={url} onChange={e=>setUrl(e.target.value)} autoCapitalize="none" spellCheck={false} placeholder="https://project.supabase.co" required/></label><label>คีย์สำหรับเผยแพร่ (Publishable key)<input value={key} onChange={e=>setKey(e.target.value)} autoCapitalize="none" spellCheck={false} autoComplete="off" placeholder="sb_publishable_…" required/></label>{error&&<p role="alert" className="admin-alert">{error}</p>}<button className="admin-primary">บันทึกการเชื่อมต่อบนเครื่องนี้</button></form>;
}
