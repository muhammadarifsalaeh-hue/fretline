import { useId, useState } from 'react';
import { LANG, t } from '@/i18n';
import { GUITARS_BY_ID, SAVED_GUITARS_BY_ID } from '@/data/guitars';
import { HOME_DISCOVERY_ASSETS } from '@/data/homeDiscoveryAssets';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { hasManufacturerRrp, publicPrice } from '@/utils/dataTrust';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { ArrowRightIcon, ChevronDownIcon, CloseIcon } from '@/components/ui/Icons';
import Reveal from '@/components/ui/Reveal';
import Switch from '@/components/ui/Switch';
import GuitarImage from '@/components/guitar/GuitarImage';
import { analyseRows } from './compareRows';
import CompareTable from './CompareTable';
import '@/styles/home-compare-premium.css';

// Both examples have licensed photographs registered to their exact catalog IDs.
// The generic electric/acoustic scene is atmosphere, never product evidence.
const EXAMPLE_IDS = ['yamaha-fg820-12', 'martin-d-28'];
const PREVIEW_ROWS = ['neck', 'body', 'fretboard', 'pickups', 'scale', 'frets', 'weight', 'price'];
const copy = (th, en) => LANG === 'en' ? en : th;

function BenefitIcon({ kind }) {
  return <svg width="27" height="27" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.35" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    {kind === 'balance' ? <><path d="M12 3v17m-4 1h8M4 7h16M7 7l-4 8h8L7 7Zm10 0-4 8h8l-4-8Z" /><path d="M3 15c0 3 8 3 8 0m2 0c0 3 8 3 8 0" /></> : kind === 'compare' ? <><path d="M4 21V11h4v10m2 0V6h4v15m2 0V3h4v18" /></> : <path d="M20.5 5.5c-2.5-2.5-6-1.5-8.5 1-2.5-2.5-6-3.5-8.5-1-3 3 0 7 8.5 14 8.5-7 11.5-11 8.5-14Z" />}
  </svg>;
}

export default function CompareSection() {
  const { compare, removeCompare } = useShop();
  const [diffOnly, setDiffOnly] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const panelId = useId();
  const selected = compare.map((id) => SAVED_GUITARS_BY_ID[id]).filter(Boolean);
  const usingSelection = selected.length >= 2;
  const guitars = usingSelection ? selected : EXAMPLE_IDS.map((id) => GUITARS_BY_ID[id]).filter(Boolean);
  const fullComparisonUrl = `/compare?ids=${guitars.map((guitar) => guitar.id).join(',')}`;
  const photo = HOME_DISCOVERY_ASSETS.compareBackdrop;
  const analysed = analyseRows(guitars, { includeSamples: false, includeIdentity: false });
  const previewRows = PREVIEW_ROWS.map((key) => analysed.find(({ row }) => row.key === key))
    .filter((entry) => entry && (!diffOnly || entry.diff));

  return (
    <section id="compare" className="home-compare-section home-premium-comparison" aria-labelledby="home-compare-title">
      <div className="container-x">
        <div className="home-compare-layout">
          <Reveal className="home-experience-copy home-compare-scene">
            <div className="home-compare-scene__photo" aria-hidden="true">
              <img src={photo.src} srcSet={photo.srcSet} sizes="(min-width: 1024px) 48vw, 100vw" width={photo.width} height={photo.height} alt="" loading="lazy" decoding="async" />
            </div>
            <div className="home-compare-story">
              <p className="home-experience-eyebrow"><span aria-hidden="true" />04 / SIDE BY SIDE</p>
              <h2 id="home-compare-title">
                {t('signature.compare.titleLead')}<br /><em>{t('signature.compare.titleEnd')}</em>
              </h2>
              <p className="home-experience-description">{t('signature.compare.body')}</p>
              <Button href={fullComparisonUrl} size="lg" className="home-experience-cta">
                {t(usingSelection ? 'cmpsec.open' : 'cmpsec.start')}<ArrowRightIcon size={18} />
              </Button>
              <p className="home-compare-selection-note">{t(usingSelection ? 'cmpsec.noteSelected' : 'cmpsec.noteSample')}</p>
            </div>
            <ul className="home-compare-benefits" aria-label={copy('เปรียบเทียบเพื่อเลือกกีตาร์', 'A clearer comparison')}>
              <li><BenefitIcon kind="balance" /><span>{copy('เห็นความต่าง', 'See the details')}<br />{copy('ชัดเจน', 'that matter')}</span></li>
              <li><BenefitIcon kind="compare" /><span>{copy('เปรียบเทียบได้สูงสุด', 'Compare up to')}<br />{copy(`${MAX_COMPARE} รุ่นพร้อมกัน`, `${MAX_COMPARE} guitars together`)}</span></li>
              <li><BenefitIcon kind="heart" /><span>{copy('เลือกกีตาร์', 'Find the guitar')}<br />{copy('ที่ใช่สำหรับคุณ', 'that feels like you')}</span></li>
            </ul>
            <AppLink href="/image-credits#home-photography" className="home-compare-photo-credit">{copy('เครดิตภาพประกอบบรรยากาศ', 'Atmospheric photography credits')}</AppLink>
          </Reveal>

          <Reveal className="home-compare-preview">
            <div className="home-compare-caption">
              <div>
                <p>{t(usingSelection ? 'cmpsec.yours' : 'cmpsec.sample')}</p>
                {selected.length > 0 && <p className="home-compare-count">{t('p4.compare.count', { n: selected.length, max: MAX_COMPARE })}</p>}
              </div>
              <Switch checked={diffOnly} onChange={setDiffOnly} label={t('cmp.diffOnly')} />
            </div>

            <div
              className="home-compare-preview-scroll"
              role="region"
              aria-label={t('signature.compare.previewRegion')}
              tabIndex={0}
              style={{ '--home-compare-count': guitars.length }}
            >
              <table className="home-compare-preview-table">
                <caption className="sr-only">{t('signature.compare.previewRegion')}</caption>
                <thead>
                  <tr>
                    <th scope="col"><span className="sr-only">{t('cmp.model')}</span></th>
                    {guitars.map((guitar) => (
                      <th scope="col" key={guitar.id}>
                        <div className="home-compare-product" data-home-compare-model={guitar.id}>
                          <AppLink href={guitarUrl(guitar.slug)} className="home-compare-product__photo" aria-label={t('cmp.viewAria', { name: `${guitar.brand} ${guitar.name}` })}>
                            <GuitarImage guitar={guitar} sizes="(min-width: 1100px) 200px, (min-width: 700px) 20vw, 40vw" className="absolute inset-0" />
                          </AppLink>
                          <div className="home-compare-product__copy">
                            <span className="home-compare-brand">{guitar.brand}</span>
                            <AppLink href={guitarUrl(guitar.slug)} className="home-compare-model">
                              {guitar.name}
                            </AppLink>
                          </div>
                          {usingSelection && (
                            <button
                              type="button"
                              className="home-compare-remove"
                              data-home-compare-remove={guitar.id}
                              aria-label={t('cmp.removeAria', { name: guitar.name })}
                              onClick={() => removeCompare(guitar.id)}
                            >
                              <CloseIcon size={15} />
                            </button>
                          )}
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewRows.map(({ row, diff, displayOf }) => (
                    <tr key={row.key} data-home-compare-row={row.key} className={diff ? 'is-different' : undefined}>
                      <th scope="row">{row.label}</th>
                      {guitars.map((guitar) => (
                        <td key={guitar.id} data-home-compare-value={guitar.id}>
                          {row.key === 'price' ? (
                            <>{publicPrice(guitar)}{hasManufacturerRrp(guitar) && <span className="mt-1 block text-mute">{t('pricing.rrpShort')}</span>}</>
                          ) : displayOf(guitar)}
                        </td>
                      ))}
                    </tr>
                  ))}
                  {previewRows.length === 0 && (
                    <tr><td colSpan={guitars.length + 1} className="home-compare-no-differences">{t('p4.compare.noDifferences')}</td></tr>
                  )}
                </tbody>
              </table>
            </div>

            <p className="home-compare-source-note">{t('signature.compare.sourceNote')}</p>
            <button
              type="button"
              className="home-compare-expand"
              data-home-compare-expand
              aria-expanded={expanded}
              aria-controls={panelId}
              onClick={() => setExpanded((value) => !value)}
            >
              <span>{t(expanded ? 'signature.compare.collapse' : 'signature.compare.expand')}</span>
              <ChevronDownIcon size={18} />
            </button>
            <AppLink href={fullComparisonUrl} className="home-compare-page-link">{t('cmpsec.open')}<ArrowRightIcon size={16} /></AppLink>
          </Reveal>
        </div>

        <div id={panelId} className="home-compare-expanded" data-home-compare-panel hidden={!expanded}>
          {expanded && (
            <>
              <p className="home-compare-scroll-hint">{t('p4.compare.scrollHint')}</p>
              <CompareTable
                guitars={guitars}
                diffOnly={diffOnly}
                onRemove={usingSelection ? removeCompare : undefined}
                includeSamples={false}
                editorial
                grouped
              />
            </>
          )}
        </div>
      </div>
    </section>
  );
}
