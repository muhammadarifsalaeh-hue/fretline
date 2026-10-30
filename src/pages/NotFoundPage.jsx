import { useEffect } from 'react';
import Button from '@/components/ui/Button';

export default function NotFoundPage() {
  useEffect(() => {
    document.title = 'ไม่พบหน้านี้ — Fretline';
  }, []);
  return (
    <section className="signature-not-found container-x flex min-h-[70svh] flex-col items-start justify-center pt-28">
      <p className="font-mono text-sm text-gold">404</p>
      <h1 className="mt-3 font-serif text-5xl leading-none tracking-tight md:text-7xl">ไม่พบหน้าที่คุณกำลังค้นหา</h1>
      <p className="mt-5 max-w-md text-mute">หน้านี้อาจถูกย้าย หรือลิงก์อาจไม่ถูกต้อง</p>
      <div className="mt-8 flex gap-3">
        <Button href="/guitars">เลือกกีตาร์</Button>
        <Button href="/" variant="ghost">กลับหน้าหลัก</Button>
      </div>
    </section>
  );
}
