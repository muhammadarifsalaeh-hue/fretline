import { normalizeGuitarIds } from '@/utils/selection';
import { t } from '@/i18n';
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

const ShopContext = createContext(null);
export const MAX_COMPARE = 4;

// state ที่จำค่าไว้ใน localStorage (รีเฟรชแล้วรายการยังอยู่)
function usePersistedState(key, initial, limit = Infinity) {
  const [value, setValue] = useState(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? normalizeGuitarIds(JSON.parse(raw), limit) : initial;
    } catch {
      return initial;
    }
  });
  useEffect(() => {
    try {
      localStorage.setItem(key, JSON.stringify(value));
    } catch {
      /* ไม่เป็นไรถ้า storage ใช้ไม่ได้ */
    }
  }, [key, value]);
  return [value, setValue];
}

export function ShopProvider({ children }) {
  const [compare, setCompare] = usePersistedState('fretline:compare', [], MAX_COMPARE);
  const [wishlist, setWishlist] = usePersistedState('fretline:wishlist', []);
  const [toast, setToast] = useState(null);
  const timer = useRef(0);
  useEffect(() => () => window.clearTimeout(timer.current), []);

  const notify = useCallback((message) => {
    setToast({ message, id: Date.now() });
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setToast(null), 2400);
  }, []);

  const toggleCompare = useCallback(
    (guitar) => {
      if (compare.includes(guitar.id)) {
        setCompare((previous) => previous.filter((id) => id !== guitar.id));
        notify(t('toast.compareRemoved', { name: guitar.name }));
        return;
      }
      if (compare.length >= MAX_COMPARE) {
        notify(t('toast.compareMax', { n: MAX_COMPARE }));
        return;
      }
      setCompare((previous) => previous.includes(guitar.id) || previous.length >= MAX_COMPARE ? previous : [...previous, guitar.id]);
      notify(t('toast.compareAdded', { name: guitar.name }));
    },
    [compare, notify, setCompare],
  );

  const toggleWishlist = useCallback(
    (guitar) => {
      if (wishlist.includes(guitar.id)) {
        setWishlist((previous) => previous.filter((id) => id !== guitar.id));
        notify(t('toast.wishRemoved', { name: guitar.name }));
      } else {
        setWishlist((previous) => previous.includes(guitar.id) ? previous : [...previous, guitar.id]);
        notify(t('toast.wishSaved', { name: guitar.name }));
      }
    },
    [wishlist, notify, setWishlist],
  );

  const clearWishlist = useCallback(() => {
    setWishlist([]);
    notify(t('toast.wishCleared'));
  }, [notify, setWishlist]);
  const clearCompare = useCallback(() => setCompare([]), [setCompare]);
  const setCompareIds = useCallback((ids) => {
    const next = normalizeGuitarIds(ids, MAX_COMPARE);
    setCompare((previous) => previous.length === next.length && previous.every((id, index) => id === next[index]) ? previous : next);
  }, [setCompare]);

  const removeCompare = useCallback((id) => setCompare((prev) => prev.filter((x) => x !== id)), [setCompare]);

  const value = useMemo(
    () => ({ compare, wishlist, toast, notify, toggleCompare, toggleWishlist, removeCompare, clearCompare, setCompareIds, clearWishlist }),
    [compare, wishlist, toast, notify, toggleCompare, toggleWishlist, removeCompare, clearCompare, setCompareIds, clearWishlist],
  );

  return <ShopContext.Provider value={value}>{children}</ShopContext.Provider>;
}

export function useShop() {
  const ctx = useContext(ShopContext);
  if (!ctx) throw new Error('useShop must be used inside <ShopProvider>');
  return ctx;
}
