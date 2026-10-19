import { useEffect } from 'react';

/**
 * Parallax เบา ๆ ตามเมาส์และการ scroll — ปิดอัตโนมัติถ้าผู้ใช้ตั้ง reduced motion
 * ผูกกับ element ผ่าน ref (ควรเป็น wrapper ที่ไม่มี transform อื่นซ้อน)
 */
export default function useParallax(ref, { mouse = 12, scroll = 0.06 } = {}) {
  useEffect(() => {
    const el = ref.current;
    if (!el) return undefined;
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return undefined;

    let mx = 0;
    let my = 0;
    let sy = 0;
    let raf = 0;

    const apply = () => {
      raf = 0;
      el.style.transform = `translate3d(${mx}px, ${my + sy}px, 0)`;
    };
    const schedule = () => {
      if (!raf) raf = requestAnimationFrame(apply);
    };
    const onMove = (e) => {
      mx = -(e.clientX / window.innerWidth - 0.5) * mouse * 2;
      my = -(e.clientY / window.innerHeight - 0.5) * mouse * 2;
      schedule();
    };
    const onScroll = () => {
      sy = window.scrollY * scroll;
      schedule();
    };

    window.addEventListener('mousemove', onMove, { passive: true });
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('scroll', onScroll);
      if (raf) cancelAnimationFrame(raf);
    };
  }, [ref, mouse, scroll]);
}
