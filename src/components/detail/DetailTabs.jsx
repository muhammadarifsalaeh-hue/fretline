import { useEffect, useId, useRef, useState } from 'react';
import { useLocation } from 'react-router-dom';
import { t } from '@/i18n';
import DataStatusNote from './DataStatusNote';
import SpecTable from './SpecTable';
import { NOT_SPECIFIED } from '@/utils/format';

export default function DetailTabs({ guitar, keyFeatures }) {
  const { hash } = useLocation();
  const [active, setActive] = useState(hash === '#specs' ? 'specs' : 'overview');
  useEffect(() => {
    if (hash === '#specs') setActive('specs');
  }, [hash]);
  useEffect(() => {
    if (hash !== '#specs' || active !== 'specs') return undefined;
    const frame = requestAnimationFrame(() => document.getElementById('specs')?.scrollIntoView({ block: 'start' }));
    return () => cancelAnimationFrame(frame);
  }, [hash, active]);
  const id = useId();
  const refs = useRef({});
  const tabs = [
    { id: 'overview', label: t('detail.overviewTab') },
    { id: 'specs', label: t('detail.specs') },
    { id: 'reviews', label: t('detail.reviewsTab') },
  ];
  const onKey = (event, index) => {
    let next;
    if (event.key === 'ArrowRight') next = (index + 1) % tabs.length;
    if (event.key === 'ArrowLeft') next = (index - 1 + tabs.length) % tabs.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = tabs.length - 1;
    if (next === undefined) return;
    event.preventDefault(); setActive(tabs[next].id); refs.current[tabs[next].id]?.focus();
  };
  return (
    <section className="detail-information container-x" aria-label={t('detail.about')}>
      <div role="tablist" aria-label={t('detail.about')} className="detail-tabs">
        {tabs.map((tab, index) => (
          <button key={tab.id} ref={(element) => { refs.current[tab.id] = element; }} type="button" role="tab"
            id={`${id}-${tab.id}-tab`} aria-controls={`${id}-${tab.id}-panel`} aria-selected={active === tab.id}
            tabIndex={active === tab.id ? 0 : -1} onKeyDown={(event) => onKey(event, index)} onClick={() => setActive(tab.id)}>{tab.label}</button>
        ))}
      </div>
      {tabs.map((tab) => (
        <div key={tab.id} role="tabpanel" id={`${id}-${tab.id}-panel`} aria-labelledby={`${id}-${tab.id}-tab`}
          tabIndex={0} hidden={active !== tab.id} className="detail-tab-panel">
          {tab.id === 'overview' && (
            <div className="grid gap-8 md:grid-cols-[1.35fr_1fr]">
              <div>
                <h2 className="mb-4 text-lg font-medium">{t('detail.about')} {guitar.name}</h2>
                <DataStatusNote guitar={guitar} />
                <p className="text-sm leading-8 text-bone/75">{guitar.description || NOT_SPECIFIED}</p>
              </div>
              <dl className="detail-key-features">
                {keyFeatures.map((feature) => <div key={feature.label}><dt>{feature.label}</dt><dd>{feature.value}</dd></div>)}
              </dl>
            </div>
          )}
          {tab.id === 'specs' && <div id="specs"><DataStatusNote guitar={guitar} /><SpecTable guitar={guitar} /></div>}
          {tab.id === 'reviews' && (
            <div className="review-empty">
              <span aria-hidden="true" className="text-3xl text-gold">◇</span>
              <h2 className="mt-3 text-lg font-medium">{t('detail.noVerifiedReviews')}</h2>
              <p className="mt-2 max-w-lg text-sm leading-7 text-mute">{t('detail.reviewExplanation')}</p>
            </div>
          )}
        </div>
      ))}
    </section>
  );
}
