import { useLocation } from 'react-router-dom';
import '@/styles/signature/index.css';

// Presentation boundary only. Auth, catalog hydration and all route contracts
// remain owned by the original application. Admin never inherits this theme.
export default function PublicExperience({ children }) {
  const { pathname } = useLocation();
  const admin = pathname === '/admin' || pathname.startsWith('/admin/');
  const page = pathname === '/' ? 'home'
    : pathname.startsWith('/guitars/') ? 'detail'
      : pathname === '/guitars' ? 'catalog'
        : pathname.startsWith('/brands/') ? 'brand'
          : ({ '/brands': 'brands', '/compare': 'compare', '/find-my-guitar': 'quiz', '/wishlist': 'favorites', '/practice': 'practice', '/image-credits': 'credits', '/qr': 'qr' })[pathname] ?? 'other';
  return <div className={admin ? 'admin-original-experience' : 'fretline-signature'} data-experience-page={page}>{children}</div>;
}
