import { cn } from '@/utils/cn';
import { CheckIcon } from '@/components/ui/Icons';

/**
 * ตัวเลือกคำตอบ (radio ที่เข้าถึงได้ด้วยคีย์บอร์ด)
 * คลิก/แตะ → ไปข้อถัดไปอัตโนมัติ | ใช้ลูกศรคีย์บอร์ดเลือกโดยไม่เด้งข้าม แล้วกด Next
 */
export default function QuizOption({ name, option, checked, onSelect, className = '' }) {
  return (
    <label
      className={cn(
        'group relative flex cursor-pointer flex-col gap-2 rounded-2xl border p-5 transition duration-300 ease-premium sm:p-6',
        checked ? 'border-gold bg-gold/[0.07]' : 'border-line bg-surface hover:-translate-y-0.5 hover:border-white/30',
        className,
      )}
    >
      <input
        type="radio"
        name={name}
        value={option.value}
        checked={checked}
        onChange={() => {}}
        onClick={(e) => onSelect(option.value, e.detail > 0)}
        className="peer sr-only"
      />
      <span
        aria-hidden="true"
        className="pointer-events-none absolute inset-0 rounded-2xl peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-gold"
      />
      <span className="flex items-start justify-between gap-4">
        <span className="font-serif text-2xl leading-tight sm:text-[1.7rem]">{option.label}</span>
        <span
          aria-hidden="true"
          className={cn(
            'mt-1 grid h-6 w-6 shrink-0 place-items-center rounded-full border transition duration-300',
            checked ? 'border-gold bg-gold text-ink' : 'border-white/20 text-transparent group-hover:border-white/40',
          )}
        >
          <CheckIcon size={14} strokeWidth={2.4} />
        </span>
      </span>
      <span className="text-sm leading-relaxed text-mute">{option.desc}</span>
    </label>
  );
}
