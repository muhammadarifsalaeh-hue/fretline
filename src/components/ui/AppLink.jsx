import { Link } from 'react-router-dom';

/**
 * ลิงก์เดียวใช้ได้ทุกกรณี
 *  - '/guitars'  → ลิงก์ภายในผ่าน router (ไม่โหลดหน้าใหม่)
 *  - '#featured' หรือ URL ภายนอก → <a> ปกติ
 */
export default function AppLink({ href, children, ...props }) {
  if (href && href.startsWith('/')) {
    return (
      <Link to={href} {...props}>
        {children}
      </Link>
    );
  }
  return (
    <a href={href} {...props}>
      {children}
    </a>
  );
}
