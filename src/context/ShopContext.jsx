import { t } from '@/i18n';
import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from 'react';

const ShopContext = createContext(null);
export const MAX_COMPARE = 4;

// state ที่จำค่าไว้ใน localStorage (รีเฟรชแล้วรายการยังอยู่)
function usePersistedState(key, initial) {
  const [value, setValue] = useState(() => {
    try {
      const raw = localStorage.getItem(key);
      return raw ? JSON.parse(raw) : initial;
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
  const [compare, setCompare] = usePersistedState('fretline:compare', []);
  const [wishlist, setWishlist] = usePersistedState('fretline:wishlist', []);
  const [toast, setToast] = useState(null);
  const timer = useRef(0);

  const notify = useCallback((message) => {
    setToast({ message, id: Date.now() });
    window.clearTimeout(timer.current);
    timer.current = window.setTimeout(() => setToast(null), 2400);
  }, []);

  const toggleCompare = useCallback(
    (guitar) => {
      if (compare.includes(guitar.id)) {
        setCompare(compare.filter((id) => id !== guitar.id));
        notify(t('toast.compareRemoved', { name: guitar.name }));
        return;
      }
      if (compare.length >= MAX_COMPARE) {
        notify(t('toast.compareMax', { n: MAX_COMPARE }));
        return;
      }
      setCompare([...compare, guitar.id]);
      notify(t('toast.compareAdded', { name: guitar.name }));
    },
    [compare, notify, setCompare],
  );

  const toggleWishlist = useCallback(
    (guitar) => {
      if (wishlist.includes(guitar.id)) {
        setWishlist(wishlist.filter((id) => id !== guitar.id));
        notify(t('toast.wishRemoved', { name: guitar.name }));
      } else {
        setWishlist([...wishlist, guitar.id]);
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
  const setCompareIds = useCallback((ids) => setCompare(ids.slice(0, MAX_COMPARE)), [setCompare]);

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
