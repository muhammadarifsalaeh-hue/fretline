import gallery from 'virtual:fretline-development-image-preview';
import { t } from '@/i18n';

// Preview-only presentation data never changes catalog colors, rights or IDs.
const preview = import.meta.env.DEV && gallery ? {
  ...gallery,
  images: gallery.images.map((image) => ({ ...image, label: image.labelKey ? t(image.labelKey) : image.label })),
} : null;
let currentPreview = preview;
const listeners = new Set();

export const subscribeDevelopmentPreview = (listener) => { listeners.add(listener); return () => listeners.delete(listener); };
export const getDevelopmentPreviewSnapshot = () => currentPreview;
export const getEmptyPreviewSnapshot = () => null;

/** Browser-owned object URLs stay in memory and never become catalog assets. */
export function setBrowserPreviewImages(images) {
  if (!import.meta.env.DEV || !preview || images.length !== 4) return false;
  const previous = currentPreview;
  currentPreview = { ...preview, images, browserLocal: true };
  for (const listener of listeners) listener();
  if (previous?.browserLocal) for (const image of previous.images) URL.revokeObjectURL(image.src);
  return true;
}

export function clearBrowserPreviewImages() {
  const previous = currentPreview;
  currentPreview = preview;
  for (const listener of listeners) listener();
  if (previous?.browserLocal) for (const image of previous.images) URL.revokeObjectURL(image.src);
}

export const getDevelopmentImagePreview = (guitar) => currentPreview?.guitarId === guitar?.id ? currentPreview : null;
export const hasDevelopmentImagePreview = (guitar) => Boolean(getDevelopmentImagePreview(guitar));

export function getDevelopmentPreviewImage(guitar, src) {
  const images = getDevelopmentImagePreview(guitar)?.images ?? [];
  return src === undefined ? images[0] : images.find((image) => image.src === src);
}
