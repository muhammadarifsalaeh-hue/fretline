import { t } from '@/i18n';

// Localize display notices; keep the original rights records and license links.
const modificationLabels = new Map([
  ['EXIF orientation applied; resized and encoded as WebP. No crop, retouch, background removal, or AI alteration.', 'targeted.images.resized'],
  ['EXIF orientation applied; metadata including GPS removed; resized without cropping and encoded as WebP. No retouch, background removal, or AI alteration. Derivatives distributed under CC BY-SA 4.0.', 'targeted.images.metadataRemoved'],
]);

/** Visible source, author, license and modifications for a genuine model photo. */
export default function ImageAttribution({ image }) {
  const rights = image?.attribution;
  if (!rights) return image?.credit ? <p className="mt-3 text-xs text-mute">{image.credit}</p> : null;
  return (
    <div className="image-attribution mt-3 text-xs leading-6 text-mute">
      {rights.caption && <p>{rights.caption}</p>}
      <p><a href={rights.sourceUrl} target="_blank" rel="noopener noreferrer">{rights.author} · {t('p6.images.source')}</a>
        {' · '}<a href={rights.licenseUrl} target="_blank" rel="noopener noreferrer">{rights.license}</a></p>
      <details><summary>{t('p6.images.changes')}</summary><p>{modificationLabels.has(rights.changes) ? t(modificationLabels.get(rights.changes)) : rights.changes}</p></details>
    </div>
  );
}
