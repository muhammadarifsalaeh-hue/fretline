import { cn } from '@/utils/cn';

/** สวิตช์เปิด/ปิดพร้อมข้อความ */
export default function Switch({ checked, onChange, label }) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="flex min-h-[44px] items-center gap-3 text-sm text-bone/85"
    >
      {label}
      <span className={cn('relative h-6 w-11 rounded-full transition-colors duration-300', checked ? 'bg-gold' : 'bg-line')}>
        <span
          className={cn(
            'absolute left-0.5 top-0.5 h-5 w-5 rounded-full shadow transition-transform duration-300 ease-premium',
            checked ? 'translate-x-5 bg-ink' : 'translate-x-0 bg-bone',
          )}
        />
      </span>
    </button>
  );
}
