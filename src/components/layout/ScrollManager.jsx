import { useEffect } from 'react';
import { focusSearch, scrollToElement, scrollToTop } from '@/utils/dom';
import { useLocation } from 'react-router-dom';

function hasOpenDialog() {
  return [...document.querySelectorAll('[role="dialog"][aria-modal="true"]')].some((dialog) => (
    !dialog.closest('[aria-hidden="true"], [inert]')
    && dialog.getClientRects().length > 0
    && window.getComputedStyle(dialog).visibility !== 'hidden'
  ));
}

/** Route changes announce the new main content; query-only filter edits keep focus. */
export default function ScrollManager() {
  const { pathname, hash } = useLocation();

  useEffect(() => {
    // DetailTabs owns activating and positioning its specs panel.
    if (hash === '#specs' && pathname.startsWith('/guitars/')) return undefined;

    const completeNavigation = () => {
      const main = document.getElementById('main-content');
      // Wait for lazy routes instead of focusing their loading skeleton.
      if (!main?.querySelector('h1') || hasOpenDialog()) return false;

      if (hash === '#search') {
        focusSearch();
        return true;
      }
      if (hash) {
        let id;
        try { id = decodeURIComponent(hash.slice(1)); } catch { return true; }
        scrollToElement(document.getElementById(id));
        return true;
      }

      scrollToTop({ behavior: 'auto' });
      // The quiz already focuses each question/result, and other pages may
      // deliberately focus a field. Do not replace that component-owned focus.
      const quizOwnsFocus = pathname === '/find-my-guitar'
        && main.querySelector('h1[tabindex="-1"], h2[tabindex="-1"]');
      if (!quizOwnsFocus && !main.contains(document.activeElement)) {
        main.focus({ preventScroll: true });
      }
      return true;
    };

    if (completeNavigation()) return undefined;
    const observer = new MutationObserver(() => {
      if (completeNavigation()) observer.disconnect();
    });
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ['aria-hidden', 'aria-busy', 'inert', 'class'],
    });
    return () => observer.disconnect();
  }, [pathname, hash]);

  return null;
}
