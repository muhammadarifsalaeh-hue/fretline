import { useEffect, useRef, useState } from 'react';
import { t } from '@/i18n';
import { useShop } from '@/context/ShopContext';

/** Keep a selectable URL available when clipboard access is denied (e.g. Safari). */
export default function ShareLink({ url, disabled = false }) {
  const { notify } = useShop();
  const [fallback, setFallback] = useState(false);
  const inputRef = useRef(null);
  useEffect(() => {
    if (fallback) { inputRef.current?.focus(); inputRef.current?.select(); }
  }, [fallback]);
  const share = async () => {
    try { await navigator.clipboard.writeText(url); notify(t('p4.linkCopied')); }
    catch { setFallback(true); }
  };
  return (
    <div className="share-link-control">
      <button type="button" onClick={share} disabled={disabled} className="phase4-button">{t('p4.share')}</button>
      {fallback && <label className="mt-2 block text-xs text-mute">{t('p4.copyManually')}
        <input ref={inputRef} readOnly value={url} onFocus={(event) => event.target.select()} className="mt-2 h-11 w-full min-w-0 rounded-lg border border-line bg-ink px-3 text-xs text-bone" />
      </label>}
    </div>
  );
}
