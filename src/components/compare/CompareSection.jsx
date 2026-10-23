import { useId, useState } from 'react';
import { t } from '@/i18n';
import { GUITARS_BY_ID, SAVED_GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { hasManufacturerRrp, publicPrice } from '@/utils/dataTrust';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { ArrowRightIcon, ChevronDownIcon, CloseIcon } from '@/components/ui/Icons';
import Reveal from '@/components/ui/Reveal';
import Switch from '@/components/ui/Switch';
import { analyseRows } from './compareRows';
import CompareTable from './CompareTable';

// Keep the existing pair when fewer than two saved guitars can be compared.
const EXAMPLE_IDS = ['fender-american-professional-ii-stratocaster', 'gibson-les-paul-standard-60s'];
const PREVIEW_ROWS = ['neck', 'frets', 'price', 'body', 'fretboard', 'pickups', 'scale'];

export default function CompareSection() {
  const { compare, removeCompare } = useShop();
  const [diffOnly, setDiffOnly] = useState(true);
  const [expanded, setExpanded] = useState(false);
  const panelId = useId();
  const selected = compare.map((id) => SAVED_GUITARS_BY_ID[id]).filter(Boolean);
  const usingSelection = selected.length >= 2;
  const guitars = usingSelection ? selected : EXAMPLE_IDS.map((id) => GUITARS_BY_ID[id]).filter(Boolean);
  const analysed = analyseRows(guitars, { includeSamples: false, includeIdentity: false });
  const previewRows = PREVIEW_ROWS.map((key) => analysed.find(({ row }) => row.key === key))
    .filter((entry) => entry && (!diffOnly || entry.diff)).slice(0, 3);

  return (
    <section id="compare" className="home-compare-section" aria-labelledby="home-compare-title">
      <div className="container-x">
        <div className="home-compare-layout">
          <Reveal className="home-experience-copy">
            <p className="home-experience-eyebrow"><span aria-hidden="true" />04 / SIDE BY SIDE</p>
            <h2 id="home-compare-title">
              {t('signature.compare.titleLead')}<br />{t('signature.compare.titleEnd')}
            </h2>
            <p className="home-experience-description">{t('signature.compare.body')}</p>
            <Button href="/compare" variant="ghost" size="lg" className="home-experience-cta">
              {t(usingSelection ? 'cmpsec.open' : 'cmpsec.start')}<ArrowRightIcon size={18} />
            </Button>
            <p className="home-compare-selection-note">{t(usingSelection ? 'cmpsec.noteSelected' : 'cmpsec.noteSample')}</p>
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
                        <span className="home-compare-brand">{guitar.brand}</span>
                        <AppLink href={guitarUrl(guitar.slug)} className="home-compare-model">
                          {guitar.name}
                        </AppLink>
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
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {previewRows.map(({ row, diff, displayOf }) => (
                    <tr key={row.key} className={diff ? 'is-different' : undefined}>
                      <th scope="row">{row.label}</th>
                      {guitars.map((guitar) => (
                        <td key={guitar.id}>
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
