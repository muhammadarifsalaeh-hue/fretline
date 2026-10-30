import { useEffect, useRef, useState } from 'react';
import ProductImage from '@/components/guitar/ProductImage';
import { compressImage, inspectImage } from './images';

/** Selection and preview are local; Storage is contacted only by the upload button. */
export default function AdminImageUpload({ guitarId, guitarName, disabled, remaining, onUpload, onPendingChange }) {
  const [queue, setQueue] = useState([]), [error, setError] = useState(''), [uploading, setUploading] = useState(false);
  const urls = useRef(new Set()), alive = useRef(true);
  useEffect(() => {
    alive.current = true;
    return () => { alive.current = false; urls.current.forEach((url) => URL.revokeObjectURL(url)); urls.current.clear(); };
  }, []);
  useEffect(() => { onPendingChange(queue.length > 0); }, [queue.length, onPendingChange]);
  const processing = queue.some((item) => ['checking', 'preparing'].includes(item.status));
  const ready = queue.length > 0 && queue.every((item) => item.status === 'ready');
  const update = (id, values) => { if (alive.current) setQueue((items) => items.map((item) => item.id === id ? { ...item, ...values } : item)); };
  function release(url) { if (urls.current.delete(url)) URL.revokeObjectURL(url); }
  function preview(blob) { const url = URL.createObjectURL(blob); urls.current.add(url); return url; }
  async function prepare(item, info, mode) {
    update(item.id, { status: 'preparing', info, problem: '' });
    try {
      const processed = await compressImage(item.file, { mode });
      if (!alive.current) return;
      const src = preview(processed.blob);
      release(item.src);
      update(item.id, { status: 'ready', src, info, processed });
    } catch (e) { update(item.id, { status: 'error', problem: e.message }); }
  }
  async function select(files) {
    if (!files.length || disabled || processing || uploading) return;
    setError('');
    if (files.length + queue.length > remaining) { setError(`รุ่นนี้เพิ่มได้อีก ${remaining} ภาพ รวมภาพที่รอตรวจ`); return; }
    const selected = files.map((file) => ({ id: crypto.randomUUID(), file, status: 'checking', src: null }));
    setQueue((items) => [...items, ...selected]);
    for (const item of selected) {
      try {
        const info = await inspectImage(item.file);
        if (!alive.current) return;
        if (info.square) await prepare(item, info, 'square');
        else {
          const src = preview(item.file);
          update(item.id, { status: 'needs-layout', info, src });
        }
      } catch (e) { update(item.id, { status: 'error', problem: e.message }); }
    }
  }
  function remove(item) { release(item.src); setQueue((items) => items.filter((candidate) => candidate.id !== item.id)); }
  async function submit() {
    if (!ready || disabled || uploading) return;
    setUploading(true); setError('');
    try {
      const uploaded = await onUpload(queue);
      if (!alive.current) return;
      queue.slice(0, uploaded).forEach((item) => release(item.src));
      setQueue((items) => items.filter((item) => !queue.slice(0, uploaded).some((done) => done.id === item.id)));
    } catch { if (alive.current) setError('อัปโหลดไม่สำเร็จ กรุณาลองอีกครั้ง'); }
    finally { if (alive.current) setUploading(false); }
  }
  return <section className="admin-image-upload" aria-label="ตรวจภาพก่อนอัปโหลด" data-upload-guitar-id={guitarId}>
    <p className="admin-upload-standard"><strong>ขนาดแนะนำ 1200 × 1200 px · สัดส่วน 1:1</strong></p>
    <p className="admin-muted">วางกีตาร์กลางภาพ ให้สูงประมาณ 85–90% ของภาพ เหลือพื้นที่รอบหัวและส่วนล่าง รองรับ JPG, PNG และ WebP สูงสุด 25 MB ต่อไฟล์</p>
    <p className="admin-muted">ภาพของ {guitarName} · ID: <code>{guitarId || 'ยังไม่บันทึก'}</code></p>
    <label className="admin-upload-picker" aria-disabled={disabled || processing || uploading || remaining < 1}>เลือกภาพจาก Photos หรือ Files<input className="admin-upload-file-input" type="file" accept="image/jpeg,image/png,image/webp" multiple
      disabled={disabled || processing || uploading || remaining < 1}
      onChange={(event) => { const files = [...event.target.files]; event.target.value = ''; select(files); }} /></label>
    {error && <p className="admin-alert" role="alert">{error}</p>}
    {queue.length > 0 && <>
      <p className="admin-muted">ดูตัวอย่างให้ครบแล้วกดอัปโหลด ภาพจะยังไม่เผยแพร่จนกด “เผยแพร่”</p>
      <ul className="admin-upload-queue">{queue.map((item) => <li key={item.id} data-upload-status={item.status}>
        {item.src ? <ProductImage src={item.src} width={item.processed?.width ?? item.info?.width} height={item.processed?.height ?? item.info?.height}
          alt={`ตัวอย่างก่อนอัปโหลด ${item.file.name}`} priority className="admin-image-preview" />
          : <div className="admin-image-preview" role="status">{item.status === 'error' ? 'อ่านภาพไม่ได้' : 'กำลังตรวจภาพ…'}</div>}
        <p>{item.file.name}</p>
        {item.info && <p className="admin-upload-dimensions">ต้นฉบับ {item.info.width} × {item.info.height} px</p>}
        {item.info?.small && <p className="admin-upload-warning">ภาพเล็กกว่าขนาดแนะนำ ระบบจะคงความละเอียดเดิมโดยไม่ขยายภาพ เลือกไฟล์ที่ใหญ่ขึ้นหากต้องการความคมชัดเต็มกรอบ</p>}
        {item.status === 'needs-layout' && <><p className="admin-upload-warning" role="status">ภาพนี้ไม่เป็นสัดส่วน 1:1 เลือกจัดลงกรอบดำโดยคงภาพครบทั้งตัว หรือกดนำออกแล้วเลือกภาพใหม่</p>
          <button type="button" onClick={() => prepare(item, item.info, 'pad')} disabled={disabled || processing || uploading}>จัดลงกรอบดำโดยไม่ตัดภาพ</button></>}
        {item.status === 'ready' && <p className="admin-upload-dimensions" role="status">พร้อมอัปโหลด {item.processed.width} × {item.processed.height} px · {Math.ceil(item.processed.blob.size / 1024)} KB</p>}
        {item.problem && <p className="admin-alert" role="alert">{item.problem}</p>}
        <div className="admin-actions"><button type="button" disabled={['checking', 'preparing'].includes(item.status) || uploading} onClick={() => remove(item)}>นำออกจากรายการอัปโหลด</button></div>
      </li>)}</ul>
      <button type="button" className="admin-primary" disabled={!ready || disabled || uploading} onClick={submit}>
        {uploading ? 'กำลังอัปโหลด…' : `อัปโหลด ${queue.length} ภาพที่ตรวจแล้ว`}
      </button>
    </>}
  </section>;
}
