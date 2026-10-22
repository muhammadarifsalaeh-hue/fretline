import { t } from '@/i18n';
import { HAS_CATALOG_PRICES, KNOWN_PRICE_MAX, PRICE_MAX, PRICE_MIN, PRICE_STEP } from '@/hooks/useCatalogFilters';
import { cn } from '@/utils/cn';
import { formatPrice } from '@/utils/format';

const PRESETS = [
  { label: t('preset.under10'), min: PRICE_MIN, max: 10000 },
  { label: t('preset.10to30'), min: 10000, max: 30000 },
  { label: t('preset.30to70'), min: 30000, max: 70000 },
  { label: t('preset.over70'), min: 70000, max: PRICE_MAX },
];

const THUMB = 44; // px — ต้องตรงกับ touch target ของ thumb ใน index.css

// This is a budget-control domain, not a claimed catalog price range. Its last
// position means no upper limit; reserve a step above bookmarked finite bounds
// so ArrowRight/End can always move a finite maximum to the unbounded endpoint.
export const getPriceSliderDomain = (min, max) => Math.max(100000, KNOWN_PRICE_MAX,
  ...[min, max].filter(Number.isFinite).map((value) => (Math.ceil(value / PRICE_STEP) + 1) * PRICE_STEP));

/** Slider ราคา 2 หัว + กล่องแสดงค่า + ปุ่มช่วงราคาสำเร็จรูป */
export default function PriceRange({ min, max, onChange }) {
  if (!HAS_CATALOG_PRICES) return <p className="text-xs leading-7 text-mute">{t('p6.price.noData')}</p>;
  const sliderMax = getPriceSliderDomain(min, max);
  const maxValue = Number.isFinite(max) ? max : sliderMax;
  const maxLabel = Number.isFinite(max) ? formatPrice(max) : t('price.unbounded');
  const ratio = (value) => Math.max(0, Math.min(1, (value - PRICE_MIN) / (sliderMax - PRICE_MIN)));
  const left = `calc(${THUMB / 2}px + (100% - ${THUMB}px) * ${ratio(min)})`;
  const right = `calc(${THUMB / 2}px + (100% - ${THUMB}px) * ${1 - ratio(maxValue)})`;

  return (
    <div>
      <div className="dual-range relative mt-2 h-11">
        <div aria-hidden="true" className="absolute inset-x-[22px] top-1/2 h-0.5 -translate-y-1/2 rounded-full bg-line" />
        <div aria-hidden="true" className="absolute top-1/2 h-0.5 -translate-y-1/2 rounded-full bg-gold" style={{ left, right }} />
        <input
          type="range"
          aria-label={t('price.minAria')}
          min={PRICE_MIN}
          max={sliderMax}
          step={PRICE_STEP}
          value={min}
          aria-valuetext={formatPrice(min)}
          // ถ้าสองหัวชนด้านขวา ต้องยกหัว min ขึ้นมาให้ลากได้
          style={{ zIndex: min > sliderMax - PRICE_STEP * 5 ? 5 : 3 }}
          onChange={(e) => onChange(Math.max(PRICE_MIN, Math.min(Number(e.target.value), max)), max)}
        />
        <input
          type="range"
          aria-label={t('price.maxAria')}
          min={PRICE_MIN}
          max={sliderMax}
          step={PRICE_STEP}
          value={maxValue}
          aria-valuetext={maxLabel}
          style={{ zIndex: 4 }}
          onChange={(e) => {
            const next = Number(e.target.value);
            onChange(min, next >= sliderMax ? PRICE_MAX : Math.max(next, min));
          }}
        />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-xl border border-line px-3 py-2">
          <p className="text-[13px] text-mute">{t('price.min')}</p>
          <p className="font-mono text-sm text-bone">{formatPrice(min)}</p>
        </div>
        <div className="rounded-xl border border-line px-3 py-2">
          <p className="text-[13px] text-mute">{t('price.max')}</p>
          <p className="font-mono text-sm text-bone">{maxLabel}</p>
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
                  'min-h-11 rounded-full border px-3.5 text-[13px] transition duration-300',
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
