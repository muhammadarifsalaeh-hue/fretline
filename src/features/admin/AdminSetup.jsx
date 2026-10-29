import { useEffect,useState } from 'react';
import setupURL from '../../../supabase/setup.sql?url';
import { clearConnection } from './config';

export default function AdminSetup({connection}){
  const [sql,setSQL]=useState(''),[email,setEmail]=useState(''),[message,setMessage]=useState('');
  const project=connection?`https://supabase.com/dashboard/project/${new URL(connection.url).hostname.split('.')[0]}`:null;
  useEffect(()=>{let alive=true;fetch(setupURL).then(r=>{if(!r.ok)throw Error();return r.text();}).then(s=>{if(alive)setSQL(s);}).catch(()=>{if(alive)setMessage('ดาวน์โหลด SQL ไม่สำเร็จ กรุณาลองเปิดหน้าใหม่');});return()=>{alive=false;};},[]);
  const adminSQL=`-- Run as project owner after creating the Auth user.\ninsert into public.admin_users(user_id)\nselect id from auth.users where lower(email)=lower('${email.trim().replaceAll("'","''")}')\non conflict(user_id) do update set active=true;\nselect count(*) as admin_accounts from public.admin_users where active;`;
  function copy(text){if(!navigator.clipboard){setMessage('ใช้ดาวน์โหลด SQL แล้วเปิดจาก Files แทน');return;}navigator.clipboard.writeText(text).then(()=>setMessage('คัดลอกแล้ว ไปวางใน SQL Editor ของ Supabase')).catch(()=>setMessage('คัดลอกไม่ได้ ใช้ดาวน์โหลด SQL แล้วเปิดจาก Files แทน'));}
  function downloadConfig(){
    const text=`VITE_SUPABASE_URL=${connection.url}\nVITE_SUPABASE_PUBLISHABLE_KEY=${connection.key}\nVITE_CATALOG_SOURCE=supabase\n`;
    const url=URL.createObjectURL(new Blob([text],{type:'text/plain'}));
    const a=document.createElement('a');a.href=url;a.download='.env.local';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  return <div className="admin-panel admin-setup-guide"><ol>
    <li><strong>สร้างฐานข้อมูลและนำเข้าข้อมูลเดิม</strong><p>Supabase → SQL Editor → New query วาง SQL แล้วกด Run รันซ้ำได้โดยไม่เขียนทับสินค้าที่แก้แล้ว</p><div className="admin-actions"><button type="button" disabled={!sql} onClick={()=>copy(sql)}>คัดลอก SQL ตั้งค่าทั้งหมด</button><a href={setupURL} download="fretline-setup.sql">ดาวน์โหลด SQL</a>{project&&<a href={`${project}/sql/new`} target="_blank" rel="noopener noreferrer">เปิด SQL Editor</a>}</div></li>
    <li><strong>สร้างบัญชีของคุณ</strong><p>Authentication → Users → Add user → Create new user กรอกอีเมลและตั้งรหัสผ่านใน Supabase เท่านั้น เปิด Auto Confirm User สำหรับบัญชีที่เจ้าของสร้างเอง ไม่ต้องส่งรหัสผ่านให้ผู้อื่น</p>{project&&<div className="admin-actions"><a href={`${project}/auth/users`} target="_blank" rel="noopener noreferrer">เปิด Users</a></div>}</li>
    <li><strong>อนุญาตบัญชีนี้เป็นแอดมิน</strong><label>อีเมลบัญชีที่สร้าง<input type="email" value={email} onChange={e=>setEmail(e.target.value)} placeholder="อีเมลของคุณ"/></label><button type="button" disabled={!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)} onClick={()=>copy(adminSQL)}>คัดลอก SQL กำหนดสิทธิ์</button><p>SQL Editor → New query → วาง → Run ต้องได้ admin_accounts อย่างน้อย 1 แล้วกลับมาล็อกอินที่ /admin</p></li>
    <li><strong>จำกัดการสมัครบัญชี</strong><p>Authentication → Sign In / Providers → ปิด Allow new users to sign up → Save</p></li>
    <li><strong>ตั้งค่าลิงก์เปลี่ยนรหัสผ่าน</strong><p>Authentication → URL Configuration → Site URL ใส่โดเมนเว็บ และ Redirect URLs → Add URL ใส่ URL เต็มของหน้า /admin?recovery=1 → Save changes ลิงก์นี้ต้องเปิดจาก Safari เครื่องเดียวกับที่กดขอเปลี่ยนรหัสผ่าน</p></li>
    <li><strong>เปิดข้อมูล Published ให้ทุกคน</strong><p>ทดสอบปุ่มดูข้อมูล Published ก่อน การตั้งค่าบน Safari เครื่องนี้ยังไม่เปลี่ยนเว็บของผู้เข้าชมคนอื่น นำค่าต่อไปนี้ไปตั้งที่ระบบ Hosting แล้ว Build/Deploy ใหม่: VITE_SUPABASE_URL, VITE_SUPABASE_PUBLISHABLE_KEY และ VITE_CATALOG_SOURCE=supabase</p>{connection&&<button type="button" onClick={downloadConfig}>ดาวน์โหลดการตั้งค่าเว็บไซต์</button>}</li>
  </ol>{message&&<p role="status" className="admin-notice">{message}</p>}{connection&&!connection.deployed&&<button type="button" onClick={()=>{if(confirm('ล้างการเชื่อมต่อบนเครื่องนี้? ไม่ลบข้อมูลใน Supabase')){clearConnection();location.reload();}}}>ล้างการเชื่อมต่อบนเครื่องนี้</button>}</div>;
}
