import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';

/** เปลี่ยนหน้า → เลื่อนขึ้นบนสุด | มี #hash → เลื่อนไปยัง section นั้น (เปลี่ยนแค่ filter ใน URL จะไม่เลื่อน) */
export default function ScrollManager() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    if (hash) {
      const timer = window.setTimeout(() => {
        document.getElementById(hash.slice(1))?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 60);
      return () => window.clearTimeout(timer);
    }
    window.scrollTo({ top: 0, left: 0 });
    return undefined;
  }, [pathname, hash]);

  return null;
}
