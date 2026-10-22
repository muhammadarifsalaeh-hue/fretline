import { useId, useRef, useState } from 'react';
import { t } from '@/i18n';
import useDevelopmentImagePreview from '@/hooks/useDevelopmentImagePreview';
import { clearBrowserPreviewImages, setBrowserPreviewImages } from '@/utils/developmentImagePreview';

const SLOTS = [
  { id: 'black', label: 'Black', colorId: 'black' },
  { id: 'red', label: 'Red', colorId: 'red' },
  { id: 'blue-teal', label: 'Blue / Teal', colorId: 'blue-teal' },
  { id: 'all-colors', labelKey: 'imagePreview.allColors', colorId: null },
];

function inspectLocalImage(file, slot) {
  if (file.type !== 'image/jpeg' || file.size > 8 * 1024 * 1024) return Promise.reject(new Error('invalid-image'));
  const src = URL.createObjectURL(file);
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve({ ...slot, label: slot.labelKey ? t(slot.labelKey) : slot.label,
      src, width: image.naturalWidth, height: image.naturalHeight,
      aiEdited: true, productPhotoVerified: false, originalImageRightsVerified: false });
    image.onerror = () => { URL.revokeObjectURL(src); reject(new Error('invalid-image')); };
    image.src = src;
  });
}

/** No fetch, POST, backend or persistent storage: files remain in this browser. */
export default function LocalPreviewImagePicker({ guitar, onApply }) {
  const preview = useDevelopmentImagePreview(guitar);
  const [files, setFiles] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const id = useId();
  const panel = useRef(null);
  if (!preview || (preview.images.length && !preview.browserLocal)) return null;
  const ready = SLOTS.every((slot) => files[slot.id]);
  const apply = async () => {
    if (!ready || loading) return;
    setLoading(true); setError('');
    const results = await Promise.allSettled(SLOTS.map((slot) => inspectLocalImage(files[slot.id], slot)));
    if (results.some((result) => result.status === 'rejected')) {
      for (const result of results) if (result.status === 'fulfilled') URL.revokeObjectURL(result.value.src);
      setError(t('imagePreview.pickerError'));
    } else {
      setBrowserPreviewImages(results.map((result) => result.value));
      onApply?.();
    }
    setLoading(false);
  };
  return <details ref={panel} open={!preview.browserLocal} className="local-preview-picker mt-5 rounded-xl border border-gold/25 bg-surface p-5" data-local-preview-picker>
    <summary className="cursor-pointer text-sm font-medium text-gold">{t('imagePreview.pickerTitle')}</summary>
    <p className="mt-3 text-xs leading-6 text-mute">{t('imagePreview.pickerNote')}</p>
    <div className="mt-4 grid gap-4 sm:grid-cols-2">
      {SLOTS.map((slot) => <label key={slot.id} htmlFor={`${id}-${slot.id}`} className="block text-xs text-bone">
        {slot.labelKey ? t(slot.labelKey) : slot.label}
        <input id={`${id}-${slot.id}`} type="file" accept="image/jpeg" disabled={loading}
          onChange={(event) => setFiles((previous) => ({ ...previous, [slot.id]: event.target.files?.[0] ?? null }))}
          className="mt-2 block min-h-11 w-full min-w-0 max-w-full rounded border border-line bg-ink p-2 text-[11px] text-mute" />
      </label>)}
    </div>
    {error && <p role="alert" className="mt-3 text-xs text-gold">{error}</p>}
    <div className="mt-4 flex flex-wrap gap-3">
      <button type="button" disabled={!ready || loading} onClick={apply} className="min-h-11 rounded-full bg-gold px-5 text-xs font-medium text-ink disabled:opacity-40">
        {t(loading ? 'imagePreview.pickerLoading' : 'imagePreview.pickerApply')}
      </button>
      {preview.browserLocal && <button type="button" disabled={loading} onClick={() => {
        clearBrowserPreviewImages(); setFiles({}); setError('');
        panel.current?.querySelectorAll('input[type="file"]').forEach((input) => { input.value = ''; });
        onApply?.();
      }} className="min-h-11 rounded-full border border-line px-5 text-xs text-bone">{t('imagePreview.pickerClear')}</button>}
    </div>
  </details>;
}
