import { useId, useRef } from 'react';
import { t } from '@/i18n';
import useDialogFocus from '@/hooks/useDialogFocus';

export default function ConfirmDialog({ open, onClose, onConfirm, title, description, confirmLabel = t('p4.confirmClear') }) {
  const ref = useRef(null);
  const id = useId();
  useDialogFocus(ref, open, onClose);
  if (!open) return null;
  return (
    <div className="fixed inset-0 z-[80] grid place-items-center bg-black/75 p-5" onClick={onClose}>
      <div ref={ref} role="alertdialog" aria-modal="true" aria-labelledby={`${id}-title`} aria-describedby={`${id}-text`}
        onClick={(event) => event.stopPropagation()} className="w-full max-w-md rounded-xl border border-line bg-surface p-6">
        <h2 id={`${id}-title`} className="text-xl font-medium">{title}</h2>
        <p id={`${id}-text`} className="mt-3 text-sm leading-7 text-mute">{description}</p>
        <div className="mt-6 flex flex-wrap justify-end gap-3">
          <button type="button" onClick={onClose} className="phase4-button">{t('p4.cancel')}</button>
          <button type="button" onClick={onConfirm} className="phase4-button is-gold">{confirmLabel}</button>
        </div>
      </div>
    </div>
  );
}
