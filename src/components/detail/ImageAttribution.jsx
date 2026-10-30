import { t } from '@/i18n';

/** Visible source, author, license and modifications for a genuine model photo. */
export default function ImageAttribution({ image }) {
  const rights = image?.attribution;
  if (!rights) return image?.credit ? <p className="mt-3 text-xs text-mute">{image.credit}</p> : null;
  return (
    <div className="image-attribution mt-3 text-xs leading-6 text-mute">
      {rights.caption && <p>{rights.caption}</p>}
      <p><a href={rights.sourceUrl} target="_blank" rel="noopener noreferrer">{rights.author} · {t('p6.images.source')}</a>
        {' · '}<a href={rights.licenseUrl} target="_blank" rel="noopener noreferrer">{rights.license}</a></p>
      <details><summary>{t('p6.images.changes')}</summary><p>{rights.changes}</p></details>
    </div>
  );
}
