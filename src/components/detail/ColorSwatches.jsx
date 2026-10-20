import { t } from '@/i18n';
import { cn } from '@/utils/cn';

/** เลือกสี (radio group) — แสดงชื่อสีที่เลือกอยู่ */
export default function ColorSwatches({ colors, value, onChange }) {
  if (!colors.length) return null;
  const selected = colors[value] ?? colors[0];
  const selectedIndex = Math.max(0, colors.indexOf(selected));
  const onKey = (event, index) => {
    let next;
    if (event.key === 'ArrowRight' || event.key === 'ArrowDown') next = (index + 1) % colors.length;
    if (event.key === 'ArrowLeft' || event.key === 'ArrowUp') next = (index - 1 + colors.length) % colors.length;
    if (event.key === 'Home') next = 0;
    if (event.key === 'End') next = colors.length - 1;
    if (next === undefined) return;
    event.preventDefault();
    onChange(next);
    event.currentTarget.parentElement.querySelectorAll('[role="radio"]')[next]?.focus();
  };
  return (
    <div>
      <p className="mb-3 text-sm text-mute">
        {t('detail.color')} <span className="ml-1 text-bone">{selected.name}</span>
      </p>
      <div role="radiogroup" aria-label={t('detail.colors')} className="flex flex-wrap gap-3">
        {colors.map((c, i) => (
          <button
            key={c.name}
            type="button"
            role="radio"
            aria-checked={i === selectedIndex}
            tabIndex={i === selectedIndex ? 0 : -1}
            aria-label={c.name}
            title={c.name}
            onClick={() => onChange(i)}
            onKeyDown={(event) => onKey(event, i)}
            className={cn(
              'grid h-11 w-11 place-items-center rounded-full border transition duration-300',
              i === selectedIndex ? 'border-gold' : 'border-white/15 hover:border-white/40',
            )}
          >
            <span
              className={cn('block h-8 w-8 rounded-full ring-1 ring-inset ring-white/20', !c.hex && 'bg-gradient-to-br from-white/25 to-white/5')}
              style={c.hex ? { background: c.hex } : undefined}
            />
          </button>
        ))}
      </div>
    </div>
  );
}
