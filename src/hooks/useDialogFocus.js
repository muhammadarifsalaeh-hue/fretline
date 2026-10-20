import { useEffect } from 'react';

/** Contain modal focus, restore the opener, and preserve the previous scroll lock. */
export default function useDialogFocus(ref, open, onClose) {
  useEffect(() => {
    if (!open || !ref.current) return undefined;
    const previous = document.activeElement;
    const overflow = document.body.style.overflow;
    const dialog = ref.current;
    const focusable = () => [...dialog.querySelectorAll('a[href],button:not([disabled]),input:not([disabled]),select:not([disabled]),summary,[tabindex="0"]')]
      .filter((element) => element.getClientRects().length > 0 && !element.closest('[inert]')
        && window.getComputedStyle(element).visibility === 'visible');
    document.body.style.overflow = 'hidden';
    focusable()[0]?.focus({ preventScroll: true });
    // A persistent drawer can still have computed visibility:hidden during
    // this effect. Retry after layout without overriding a dialog's own
    // autofocus (for example the guitar picker's search field).
    let frame;
    const focusAfterLayout = () => {
      if (dialog.contains(document.activeElement)) return;
      const first = focusable()[0];
      if (!first) {
        frame = window.requestAnimationFrame(focusAfterLayout);
        return;
      }
      first.focus({ preventScroll: true });
    };
    frame = window.requestAnimationFrame(focusAfterLayout);
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
      window.cancelAnimationFrame(frame);
      document.body.style.overflow = overflow;
      window.removeEventListener('keydown', onKey);
      if (previous?.isConnected) previous.focus({ preventScroll: true });
    };
  }, [ref, open, onClose]);
}
