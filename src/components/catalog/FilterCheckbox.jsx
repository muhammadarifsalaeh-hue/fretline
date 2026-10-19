import { cn } from '@/utils/cn';
import { CheckIcon } from '@/components/ui/Icons';

/** ตัวเลือก checkbox พร้อมจำนวนผลลัพธ์ (เป็น 0 และยังไม่เลือก = จางลง) */
export default function FilterCheckbox({ label, count, checked, onChange }) {
  const empty = count === 0 && !checked;
  return (
    <label
      className={cn(
        'group flex min-h-[40px] cursor-pointer items-center gap-3 text-sm transition-opacity',
        empty && 'opacity-40',
      )}
    >
      <input type="checkbox" className="peer sr-only" checked={checked} onChange={onChange} />
      <span
        className={cn(
          'grid h-5 w-5 shrink-0 place-items-center rounded-md border transition duration-300',
          'peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-gold',
          checked ? 'border-gold bg-gold text-ink' : 'border-white/25 group-hover:border-gold/70',
        )}
      >
        {checked && <CheckIcon size={14} strokeWidth={2.4} />}
      </span>
      <span className={cn('flex-1 transition-colors', checked ? 'text-bone' : 'text-bone/75 group-hover:text-bone')}>{label}</span>
      <span className="font-mono text-xs text-mute">{count}</span>
    </label>
  );
}
