import { useEffect, useState } from 'react';
import QRCode from 'qrcode';
import { productionSiteUrl } from '@/features/deployment/siteUrl';
import AppLink from '@/components/ui/AppLink';
import '@/styles/qr-code.css';

export default function QRCodePage() {
  const url = productionSiteUrl();
  const [image, setImage] = useState('');
  const [message, setMessage] = useState('');
  useEffect(() => {
    document.title = 'QR Code — Fretline';
    let alive = true;
    if (url) QRCode.toDataURL(url, {
      width: 1024, margin: 4, errorCorrectionLevel: 'M', color: { dark: '#101010', light: '#ffffff' },
    }).then(data => { if (alive) setImage(data); }).catch(() => { if (alive) setMessage('สร้าง QR Code ไม่สำเร็จ กรุณาลองอีกครั้ง'); });
    return () => { alive = false; };
  }, [url]);
  async function copyLink() {
    try { await navigator.clipboard.writeText(url); setMessage('คัดลอกลิงก์แล้ว'); }
    catch { setMessage('แตะลิงก์ค้างไว้เพื่อคัดลอก'); }
  }
  return <section className="qr-page container-x" aria-labelledby="qr-title">
    <div className="qr-card">
      <p className="qr-eyebrow">FRETLINE</p>
      <h1 id="qr-title">สแกนเพื่อค้นพบเสียงที่เป็นคุณ</h1>
      {url ? <>
        <div className="qr-image">{image ? <img src={image} width="1024" height="1024" alt="QR Code สำหรับเปิดเว็บไซต์ Fretline" /> : <p role="status">กำลังสร้าง QR Code…</p>}</div>
        <a className="qr-url" href={url}>{url}</a>
        <div className="qr-actions">
          {image && <a href={image} download="fretline-qr.png">ดาวน์โหลด QR Code</a>}
          <button type="button" onClick={copyLink}>คัดลอกลิงก์</button>
        </div>
      </> : <p className="qr-pending" role="status">QR Code จะพร้อมเมื่อกำหนด URL เว็บไซต์ที่เผยแพร่แล้ว</p>}
      {message && <p role="status" className="qr-message">{message}</p>}
      <AppLink href="/" className="qr-home">กลับหน้าหลัก</AppLink>
    </div>
  </section>;
}
