import { useCallback } from 'react';
import { flushSync } from 'react-dom';
import { useNavigate } from 'react-router-dom';
import { focusSearch } from '@/utils/dom';

/** Search from every route, including pages without their own search field. */
export default function useSearchNavigation() {
  const navigate = useNavigate();
  return useCallback(() => {
    if (focusSearch()) return;
    // HomePage is eager-loaded. Commit its search input before the original
    // touch gesture ends rather than attempting focus from a delayed timer.
    flushSync(() => navigate('/#search'));
    focusSearch();
  }, [navigate]);
}
