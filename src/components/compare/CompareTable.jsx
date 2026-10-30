import { publicPrice } from '@/utils/dataTrust';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import GuitarImage from '@/components/guitar/GuitarImage';
import PriceSourceNote from '@/components/guitar/PriceSourceNote';
import AppLink from '@/components/ui/AppLink';
import { CloseIcon } from '@/components/ui/Icons';
import { t } from '@/i18n';
import { analyseRows, groupRows } from './compareRows';

/** แถว/กลุ่มที่หุบหายด้วย animation (ใช้กับ "Show differences only") */
function Collapse({ hide, children }) {
  return (
    <div
      role="presentation"
      aria-hidden={hide ? true : undefined}
      className={cn(
        'grid transition-[grid-template-rows,opacity] duration-500 ease-premium',
        hide ? 'grid-rows-[0fr] opacity-0' : 'grid-rows-[1fr] opacity-100',
      )}
    >
      <div role="presentation" className="min-h-0 overflow-y-clip">{children}</div>
    </div>
  );
}

function ModelColumnContent({ guitar: g, editorial, includeSamples, compact }) {
  return <>
    <AppLink href={guitarUrl(g.slug)} className="line-clamp-2 font-serif text-xl leading-tight transition-colors hover:text-gold">{g.name}</AppLink>
    {!compact && <p className="mt-1 font-mono text-sm text-gold">{editorial && !includeSamples ? publicPrice(g) : formatPrice(g.price)}</p>}
    {!compact && <PriceSourceNote guitar={g} />}
    {g.archived && <p className="archive-label">{t('p7.archive.label')}</p>}
    {editorial && !compact && <><p className="compare-model-status">{t(`status.${g.dataStatus ?? 'sample'}`)}</p><AppLink href={guitarUrl(g.slug)} className="compare-detail-link">{t('card.view')}</AppLink></>}
  </>;
}

/**
 * ตารางเปรียบเทียบ 2–4 ตัว
 *  - แถวที่ "ต่างกัน" ไฮไลต์และข้อความสว่าง, แถวที่เหมือนกันจางลง (หรือซ่อนด้วย diffOnly)
 *  - จุดสีทอง = ค่าที่ดีที่สุดในแถว, ข้อความเล็กใต้ค่า = ส่วนต่างจากรุ่นที่ดีที่สุด
 *  - Mobile: เลื่อนแนวนอน คอลัมน์ป้ายชื่อ sticky | Desktop (lg+): แถวชื่อรุ่น sticky ใต้ Navbar
 *  - grouped: แสดงหัวข้อกลุ่ม | stickyNames: ให้แถวชื่อรุ่นติดด้านบนตอนเลื่อน
 */
export default function CompareTable({ guitars, diffOnly = false, onRemove, bg = 'bg-ink', grouped = false, stickyNames = false, includeSamples = true, editorial = false, compact = false, rowFilter }) {
  const n = guitars.length;
  const columns = `var(--label-w) repeat(${n}, minmax(var(--col-min), 1fr))`;
  const analysed = analyseRows(guitars, { includeSamples, includeIdentity: editorial });
  const groups = groupRows(rowFilter ? analysed.filter(({ row }) => rowFilter(row)) : analysed);

  return (
    <div role="region" aria-label={t('p4.compare.tableRegion')} tabIndex={0} className="compare-table-scroll overflow-x-auto [--col-min:150px] [--label-w:88px] [scrollbar-width:thin] md:[--col-min:190px] md:[--label-w:120px] lg:overflow-visible">
      <div style={{ minWidth: compact ? `calc(var(--label-w) + ${n} * var(--col-min))` : `calc(var(--label-w) + ${n} * (var(--col-min) + 1rem))` }}>
        {/* รูป + แบรนด์ */}
        {!compact && <div className="grid items-end gap-4 pb-5" style={{ gridTemplateColumns: columns }}>
          <div className={cn('sticky left-0 z-10 self-stretch', bg)} />
          {guitars.map((g) => (
            <div key={g.id} className="relative min-w-0">
              <AppLink href={guitarUrl(g.slug)} className="block" aria-label={t('cmp.viewAria', { name: `${g.brand} ${g.name}` })}>
                <GuitarImage guitar={g} sizes="(min-width: 768px) 190px, 150px" className="aspect-square rounded-2xl" />
              </AppLink>
              {onRemove && (
                <button
                  type="button"
                  data-compare-remove={g.id}
                  onClick={() => onRemove(g.id)}
                  aria-label={t('cmp.removeAria', { name: g.name })}
                  className="absolute right-2 top-2 grid h-11 w-11 place-items-center rounded-full bg-ink/75 text-bone backdrop-blur transition hover:bg-ink"
                >
                  <CloseIcon size={16} />
                </button>
              )}
              <p className="mt-3 text-xs uppercase tracking-[0.14em] text-mute">{g.brand}</p>
            </div>
          ))}
        </div>}

        <div role="table" aria-label={t('p4.compare.table')} aria-colcount={n + 1} data-compact-comparison={compact ? true : undefined}>
        {/* ชื่อรุ่น + ราคา (sticky บน Desktop) */}
        <div
          role="row"
          className={cn(
            'grid items-start gap-4 border-y border-line py-4',
            stickyNames && 'lg:sticky lg:top-20 lg:z-20 lg:bg-ink/95 lg:backdrop-blur-xl',
          )}
          style={{ gridTemplateColumns: columns }}
        >
          <div role="columnheader" className={cn('sticky left-0 z-10 text-sm text-mute lg:bg-transparent', bg)}>{t('cmp.model')}</div>
          {guitars.map((g) => (
            <div key={g.id} role="columnheader" className={cn('min-w-0', compact && 'pc-table-model')}>
              {compact ? <>
                <GuitarImage guitar={g} alt="" size="sm" className="pc-table-model__image" sizes="48px" />
                <div><span className="pc-table-model__brand">{g.brand}</span><ModelColumnContent guitar={g} editorial={editorial} includeSamples={includeSamples} compact /></div>
              </> : <ModelColumnContent guitar={g} editorial={editorial} includeSamples={includeSamples} />}
            </div>
          ))}
        </div>

        {/* สเปกแบ่งกลุ่ม */}
        {groups.map((group) => {
          const groupHidden = diffOnly && group.rows.every((r) => !r.diff);
          return (
            <div key={group.title} role="rowgroup" aria-hidden={groupHidden ? true : undefined}>
              {grouped && (
                <Collapse hide={groupHidden}>
                  <div role="row"><h3 role="columnheader" aria-colspan={n + 1} className="sticky left-0 w-max pb-3 pt-10 font-serif text-2xl text-bone">{group.title}</h3></div>
                </Collapse>
              )}
              {group.rows.map(({ row, same, diff, incomplete, best, valueOf, displayOf, allowed }) => (
                <Collapse key={row.key} hide={diffOnly && !diff}>
                  <div
                    role="row"
                    data-compare-row={row.key}
                    data-compare-different={diff || undefined}
                    data-compare-incomplete={incomplete || undefined}
                    className={cn('grid items-start gap-4 border-t border-line py-4 text-sm', diff && 'bg-white/[0.03]')}
                    style={{ gridTemplateColumns: columns }}
                  >
                    <div role="rowheader" className={cn('comparison-row-label sticky left-0 z-10 pr-2', diff ? 'bg-[#101010] text-bone' : `${bg} text-secondary`)}>
                      {row.label}
                      {same && <span className="comparison-same-note mt-1 block text-[13px] leading-relaxed text-mute">{t('cmp.same')}</span>}
                    </div>
                    {guitars.map((g) => {
                      const value = valueOf(g);
                      const isBest = best !== null && value === best;
                      const note = value != null && diff && row.note && allowed(g) ? row.note(g, guitars.filter((item) => allowed(item) && valueOf(item) != null)) : null;
                      return (
                        <div key={g.id} role="cell" className={cn('comparison-value min-w-0 break-words font-mono text-[13px] leading-relaxed', value == null ? 'text-mute' : diff ? 'text-bone' : 'text-secondary')}>
                          {isBest && (
                            <span
                              title={t('cmp.bestTitle')}
                              className="mr-2 inline-block h-1.5 w-1.5 -translate-y-px rounded-full bg-gold align-middle"
                            />
                          )}
                          {displayOf(g)}
                          {note && <span className="comparison-value-note mt-1 block text-[13px] leading-relaxed text-mute">{note}</span>}
                        </div>
                      );
                    })}
                  </div>
                </Collapse>
              ))}
            </div>
          );
        })}
        </div>
      </div>
    </div>
  );
}
