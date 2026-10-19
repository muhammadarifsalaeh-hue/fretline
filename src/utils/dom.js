// เลื่อนขึ้นบนสุดแล้ว focus ช่องค้นหา (หน้า Catalog หรือ Hero)
export function focusSearch() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
  window.setTimeout(() => {
    const el = document.getElementById('catalog-search') || document.getElementById('brands-search') || document.getElementById('hero-search');
    el?.focus({ preventScroll: true });
  }, 350);
}
