import { t } from '@/i18n';
import { PRICE_MAX, PRICE_MIN, PRICE_STEP } from '@/hooks/useCatalogFilters';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';

const PRESETS = [
  { label: t('preset.under10'), min: PRICE_MIN, max: 10000 },
  { label: t('preset.10to30'), min: 10000, max: 30000 },
  { label: t('preset.30to70'), min: 30000, max: 70000 },
  { label: t('preset.over70'), min: 70000, max: PRICE_MAX },
];

const THUMB = 22; // px — ต้องตรงกับ CSS ใน index.css

/** Slider ราคา 2 หัว + กล่องแสดงค่า + ปุ่มช่วงราคาสำเร็จรูป */
export default function PriceRange({ min, max, onChange }) {
  const ratio = (v) => (v - PRICE_MIN) / (PRICE_MAX - PRICE_MIN);
  const left = `calc(${THUMB / 2}px + (100% - ${THUMB}px) * ${ratio(min)})`;
  const right = `calc(${THUMB / 2}px + (100% - ${THUMB}px) * ${1 - ratio(max)})`;

  return (
    <div>
      <div className="dual-range relative mt-2 h-[22px]">
        <div aria-hidden="true" className="absolute inset-x-[11px] top-1/2 h-0.5 -translate-y-1/2 rounded-full bg-line" />
        <div aria-hidden="true" className="absolute top-1/2 h-0.5 -translate-y-1/2 rounded-full bg-gold" style={{ left, right }} />
        <input
          type="range"
          aria-label={t('price.minAria')}
          min={PRICE_MIN}
          max={PRICE_MAX}
          step={PRICE_STEP}
          value={min}
          // ถ้าสองหัวชนด้านขวา ต้องยกหัว min ขึ้นมาให้ลากได้
          style={{ zIndex: min > PRICE_MAX - PRICE_STEP * 5 ? 5 : 3 }}
          onChange={(e) => onChange(Math.max(PRICE_MIN, Math.min(Number(e.target.value), max)), max)}
        />
        <input
          type="range"
          aria-label={t('price.maxAria')}
          min={PRICE_MIN}
          max={PRICE_MAX}
          step={PRICE_STEP}
          value={max}
          style={{ zIndex: 4 }}
          onChange={(e) => onChange(min, Math.min(PRICE_MAX, Math.max(Number(e.target.value), min)))}
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-line px-3 py-2">
          <p className="text-[11px] text-mute">{t('price.min')}</p>
          <p className="font-mono text-sm text-bone">{formatPrice(min)}</p>
        </div>
        <div className="rounded-xl border border-line px-3 py-2">
          <p className="text-[11px] text-mute">{t('price.max')}</p>
          <p className="font-mono text-sm text-bone">{formatPrice(max)}</p>
        </div>
      </div>

      <ul className="mt-4 flex flex-wrap gap-2">
        {PRESETS.map((p) => {
          const active = p.min === min && p.max === max;
          return (
            <li key={p.label}>
              <button
                type="button"
                aria-pressed={active}
                onClick={() => onChange(p.min, p.max)}
                className={cn(
                  'min-h-[36px] rounded-full border px-3.5 text-[13px] transition duration-300',
                  active ? 'border-gold bg-gold/10 text-gold' : 'border-white/[0.12] text-bone/75 hover:border-gold hover:text-gold',
                )}
              >
                {p.label}
              </button>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
