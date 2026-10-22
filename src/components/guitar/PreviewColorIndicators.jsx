import useDevelopmentImagePreview from '@/hooks/useDevelopmentImagePreview';
import { t } from '@/i18n';

/** Gallery colors describe the supplied images, not manufacturer availability. */
export default function PreviewColorIndicators({ guitar }) {
  const preview = useDevelopmentImagePreview(guitar);
  const colors = preview?.images.length ? preview.colors : guitar.gallery?.flatMap((image) => image.color ? [image.color] : []);
  if (!colors?.length) return null;
  return <div className="mt-3 flex items-center gap-2" data-preview-color-indicators data-gallery-color-indicators>
    <ul className="flex gap-1.5" aria-label={t('artwork.colorList')}>
      {colors.map((color) => <li key={color.id} title={color.name}>
        <span className="block h-3 w-3 rounded-full ring-1 ring-inset ring-white/30" style={{ background: color.hex }} />
        <span className="sr-only">{color.name}</span>
      </li>)}
    </ul>
    <span className="text-[10px] text-mute">{t('artwork.colorCount', { n: colors.length })}</span>
  </div>;
}
