import { useEffect } from 'react';

/** Contain modal focus, restore the opener, and preserve the previous scroll lock. */
export default function useDialogFocus(ref, open, onClose) {
  useEffect(() => {
    if (!open || !ref.current) return undefined;
    const previous = document.activeElement;
    const overflow = document.body.style.overflow;
    const dialog = ref.current;
    const focusable = () => [...dialog.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),summary,[tabindex="0"]')]
      .filter((element) => element.getClientRects().length > 0 && !element.closest('[inert]'));
    document.body.style.overflow = 'hidden';
    focusable()[0]?.focus({ preventScroll: true });
    const onKey = (event) => {
      if (event.key === 'Escape') { event.preventDefault(); onClose(); }
      if (event.key !== 'Tab') return;
      const elements = focusable();
      const first = elements[0];
      const last = elements[elements.length - 1];
      if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
        event.preventDefault(); last?.focus();
      } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
        event.preventDefault(); first?.focus();
      }
    };
    window.addEventListener('keydown', onKey);
    return () => {
      document.body.style.overflow = overflow;
      window.removeEventListener('keydown', onKey);
      if (previous?.isConnected) previous.focus({ preventScroll: true });
    };
  }, [ref, open, onClose]);
}
