export default function CatalogUnavailable() {
  return <section className="container-x min-h-screen py-24" role="alert">
    <h1 className="text-2xl">โหลดข้อมูลกีตาร์ไม่สำเร็จ</h1>
    <p className="mt-4 text-mute">กรุณาตรวจการเชื่อมต่อแล้วลองอีกครั้ง</p>
    <button className="mt-6 min-h-12 rounded-lg bg-gold px-6 text-ink" onClick={() => window.location.reload()}>ลองอีกครั้ง</button>
  </section>;
}
