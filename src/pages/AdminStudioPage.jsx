import { useEffect } from 'react';
import AppLink from '@/components/ui/AppLink';
import { ArrowUpRightIcon, ShieldIcon } from '@/components/ui/Icons';
import '@/styles/admin-studio.css';

/** Setup entry only. Authentication and writes stay unavailable until Phase 2. */
export default function AdminStudioPage() {
  useEffect(() => { document.title = 'Admin Studio — Fretline'; }, []);

  return (
    <section className="admin-setup container-x" aria-labelledby="admin-title">
      <header className="admin-setup-heading">
        <p className="admin-setup-eyebrow">FRETLINE / OWNER WORKSPACE</p>
        <h1 id="admin-title">Admin Studio</h1>
        <p>พื้นที่ดูแลภาพ ราคา และสเปกกีตาร์ของคุณ</p>
      </header>

      <div className="admin-setup-panel">
        <div className="admin-setup-symbol"><ShieldIcon size={30} /></div>
        <div className="admin-setup-content">
          <h2>รอตั้งค่า Supabase</h2>
          <p>ยังไม่ได้เชื่อมต่อฐานข้อมูล การล็อกอิน อัปโหลดภาพ และบันทึกสินค้ายังไม่เปิดใช้งาน</p>
          <ol className="admin-setup-steps">
            <li>สร้างโปรเจกต์ Supabase สำหรับ Fretline</li>
            <li>เตรียม Project URL และ Publishable key</li>
            <li>ตั้งค่าฐานข้อมูลและสิทธิ์แอดมินก่อนนำเข้าข้อมูล</li>
          </ol>
          <p className="admin-setup-security">ใช้เฉพาะคีย์สาธารณะสำหรับหน้าเว็บ ห้ามใส่ Secret key หรือ Service Role key</p>
          <div className="admin-setup-actions">
            <a href="https://supabase.com/dashboard" target="_blank" rel="noopener noreferrer" className="admin-setup-primary">
              เปิด Supabase <ArrowUpRightIcon size={18} />
            </a>
            <AppLink href="/guitars" className="admin-setup-secondary">กลับไป Catalog</AppLink>
          </div>
        </div>
      </div>
    </section>
  );
}
