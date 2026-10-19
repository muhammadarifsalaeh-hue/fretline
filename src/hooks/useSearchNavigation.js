import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { focusSearch } from '@/utils/dom';

/** Search from every route, including pages without their own search field. */
export default function useSearchNavigation() {
  const navigate = useNavigate();
  return useCallback(() => {
    if (document.querySelector('#catalog-search, #brands-search, #hero-search')) focusSearch();
    else navigate('/#search');
  }, [navigate]);
}
