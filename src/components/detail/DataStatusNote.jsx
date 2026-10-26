import { t } from '@/i18n';
import { ADDITIONAL_SPECIFICATIONS } from '@/data/additionalSpecifications';
import { getDevelopmentImagePreview } from '@/utils/developmentImagePreview';

const FIELD_LABELS = {
  ...Object.fromEntries(ADDITIONAL_SPECIFICATIONS.map(({ key, label }) => [`specs.${key}`, label])),
  'specs.body': 'row.body', 'specs.neck': 'row.neck', 'specs.fretboard': 'row.fingerboard',
  'specs.pickups': 'row.pickups', 'specs.bridge': 'row.bridge', 'specs.controls': 'row.controls',
  'specs.scale': 'row.scale', 'specs.scaleMm': 'row.scale', 'specs.frets': 'row.frets',
  'specs.strings': 'row.strings', 'specs.weightKg': 'row.weight', price: 'row.price',
};

/** Partial records disclose exactly what was read, including archive/index limits. */
export default function DataStatusNote({ guitar }) {
  const { dataStatus, source } = guitar;
  const link = source?.url ? <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-gold underline-offset-4 hover:underline">{source.note || source.url}</a> : null;
  const fields = [...new Set((source?.fields ?? []).flatMap((key) => FIELD_LABELS[key] ? [t(FIELD_LABELS[key])] : []))];
  let text;
  if (dataStatus === 'verified' && link) text = <>{t('note.verifiedA', { date: source.verifiedOn })}{link}</>;
  else if (dataStatus === 'partial' && link) text = <>{t('note.partialA', { date: source.verifiedOn })}{link}{t('note.partialB')}</>;
  else text = t('note.sample');
  return <div className="data-status-note mb-8 text-sm text-mute">
    <p>{text}</p>
    {guitar.intake?.batch === 'yamaha-2026-10-26' && <p className="mt-2">{t('import.pending')}</p>}
    {source?.fields && <details className="source-scope">
      <summary>{t('p6.sources.details')}</summary>
      <p>{t(`p6.sources.method.${source.method}`)}</p>
      {source.editionNote && <p>{t('p6.sources.edition')}: {source.editionNote}</p>}
      <p>{t('p6.sources.scope')}: {t('p6.sources.identity')}{fields.length ? ` · ${fields.join(' · ')}` : ''}</p>
      {source.additionalSources?.map((extra) => <p key={extra.url}><a href={extra.url} target="_blank" rel="noopener noreferrer" className="text-gold hover:underline">{extra.note}</a>{' · '}{extra.verifiedOn}</p>)}
      <p>{t('p6.sources.partial')}</p>
      {getDevelopmentImagePreview(guitar) && <p className="mt-3 border-t border-line pt-3">{t('imagePreview.provenance')}</p>}
    </details>}
  </div>;
}
