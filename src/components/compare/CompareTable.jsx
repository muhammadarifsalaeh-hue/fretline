import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';
import { guitarUrl } from '@/utils/routes';
import GuitarImage from '@/components/guitar/GuitarImage';
import AppLink from '@/components/ui/AppLink';
import { CloseIcon } from '@/components/ui/Icons';
import { t } from '@/i18n';
import { NOT_SPECIFIED } from '@/utils/format';
import { analyseRows, groupRows } from './compareRows';

/** แถว/กลุ่มที่หุบหายด้วย animation (ใช้กับ "Show differences only") */
function Collapse({ hide, children }) {
  return (
    <div
      aria-hidden={hide}
      className={cn(
        'grid transition-[grid-template-rows,opacity] duration-500 ease-premium',
        hide ? 'grid-rows-[0fr] opacity-0' : 'grid-rows-[1fr] opacity-100',
      )}
    >
      <div className="min-h-0 overflow-y-clip">{children}</div>
    </div>
  );
}

/**
 * ตารางเปรียบเทียบ 2–4 ตัว
 *  - แถวที่ "ต่างกัน" ไฮไลต์และข้อความสว่าง, แถวที่เหมือนกันจางลง (หรือซ่อนด้วย diffOnly)
 *  - จุดสีทอง = ค่าที่ดีที่สุดในแถว, ข้อความเล็กใต้ค่า = ส่วนต่างจากรุ่นที่ดีที่สุด
 *  - Mobile: เลื่อนแนวนอน คอลัมน์ป้ายชื่อ sticky | Desktop (lg+): แถวชื่อรุ่น sticky ใต้ Navbar
 *  - grouped: แสดงหัวข้อกลุ่ม | stickyNames: ให้แถวชื่อรุ่นติดด้านบนตอนเลื่อน
 */
export default function CompareTable({ guitars, diffOnly = false, onRemove, bg = 'bg-ink', grouped = false, stickyNames = false }) {
  const n = guitars.length;
  const columns = `var(--label-w) repeat(${n}, minmax(var(--col-min), 1fr))`;
  const groups = groupRows(analyseRows(guitars));

  return (
    <div className="overflow-x-auto [--col-min:150px] [--label-w:88px] [scrollbar-width:thin] md:[--col-min:190px] md:[--label-w:120px] lg:overflow-visible">
      <div style={{ minWidth: `calc(var(--label-w) + ${n} * (var(--col-min) + 1rem))` }}>
        {/* รูป + แบรนด์ */}
        <div className="grid items-end gap-4 pb-5" style={{ gridTemplateColumns: columns }}>
          <div className={cn('sticky left-0 z-10 self-stretch', bg)} />
          {guitars.map((g) => (
            <div key={g.id} className="relative min-w-0">
              <AppLink href={guitarUrl(g.slug)} className="block" aria-label={t('cmp.viewAria', { name: `${g.brand} ${g.name}` })}>
                <GuitarImage guitar={g} sizes="(min-width: 768px) 190px, 150px" className="aspect-[4/5] rounded-2xl" imgClassName="hover:scale-[1.04]" />
              </AppLink>
              {onRemove && (
                <button
                  type="button"
                  onClick={() => onRemove(g.id)}
                  aria-label={t('cmp.removeAria', { name: g.name })}
                  className="absolute right-2 top-2 grid h-10 w-10 place-items-center rounded-full bg-ink/75 text-bone backdrop-blur transition hover:bg-ink"
                >
                  <CloseIcon size={16} />
                </button>
              )}
              <p className="mt-3 text-xs uppercase tracking-[0.14em] text-mute">{g.brand}</p>
            </div>
          ))}
        </div>

        {/* ชื่อรุ่น + ราคา (sticky บน Desktop) */}
        <div
          className={cn(
            'grid items-start gap-4 border-y border-line py-4',
            stickyNames && 'lg:sticky lg:top-20 lg:z-20 lg:bg-ink/95 lg:backdrop-blur-xl',
          )}
          style={{ gridTemplateColumns: columns }}
        >
          <div className={cn('sticky left-0 z-10 text-sm text-mute lg:bg-transparent', bg)}>{t('cmp.model')}</div>
          {guitars.map((g) => (
            <div key={g.id} className="min-w-0">
              <AppLink href={guitarUrl(g.slug)} className="line-clamp-2 font-serif text-xl leading-tight transition-colors hover:text-gold">
                {g.name}
              </AppLink>
              <p className="mt-1 font-mono text-sm text-gold">{formatPrice(g.price)}</p>
            </div>
          ))}
        </div>

        {/* สเปกแบ่งกลุ่ม */}
        {groups.map((group) => {
          const groupHidden = diffOnly && group.rows.every((r) => !r.diff);
          return (
            <div key={group.title}>
              {grouped && (
                <Collapse hide={groupHidden}>
                  <h3 className="sticky left-0 w-max pb-3 pt-10 font-serif text-2xl text-bone">{group.title}</h3>
                </Collapse>
              )}
              {group.rows.map(({ row, same, diff, best }) => (
                <Collapse key={row.key} hide={diffOnly && !diff}>
                  <div
                    className={cn('grid items-start gap-4 border-t border-line py-4 text-sm', diff && 'bg-white/[0.03]')}
                    style={{ gridTemplateColumns: columns }}
                  >
                    <div className={cn('sticky left-0 z-10 pr-2', diff ? 'bg-[#101010] text-bone/80' : `${bg} text-mute`)}>
                      {row.label}
                      {same && <span className="mt-0.5 block text-[11px] text-mute/60">{t('cmp.same')}</span>}
                    </div>
                    {guitars.map((g) => {
                      const value = row.raw(g);
                      const isBest = best !== null && value === best;
                      const note = diff && row.note ? row.note(g, guitars) : null;
                      return (
                        <div key={g.id} className={cn('min-w-0 break-words font-mono text-[13px] leading-snug', diff ? 'text-bone' : 'text-bone/45')}>
                          {isBest && (
                            <span
                              title={t('cmp.bestTitle')}
                              className="mr-2 inline-block h-1.5 w-1.5 -translate-y-px rounded-full bg-gold align-middle"
                            />
                          )}
                          {row.display ? row.display(g) : (value ?? NOT_SPECIFIED)}
                          {note && <span className="mt-1 block text-[11px] text-mute">{note}</span>}
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
  );
}
