import { t } from '@/i18n';
/** ข้อความบอกสถานะข้อมูลของรุ่น: sample / partial (ตรวจบางส่วน) / verified */
export default function DataStatusNote({ guitar }) {
  const { dataStatus, source } = guitar;
  const link = source?.url ? (
    <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-gold underline-offset-4 hover:underline">
      {source.note || source.url}
    </a>
  ) : null;

  let text;
  if (dataStatus === 'verified' && link) {
    text = <>{t('note.verifiedA', { date: source.verifiedOn })}{link}</>;
  } else if (dataStatus === 'partial' && link) {
    text = (
      <>
        {t('note.partialA', { date: source.verifiedOn })}
        {link}
        {t('note.partialB')}
      </>
    );
  } else {
    text = t('note.sample');
  }
  return <p className="mb-8 text-sm text-mute">{text}</p>;
}
