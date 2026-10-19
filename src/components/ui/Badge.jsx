import { cn } from '@/utils/cn';

const STYLES = {
  NEW: 'bg-gold text-ink',
  SALE: 'bg-bone text-ink',
  LIMITED: 'border border-gold/60 bg-ink/60 text-gold backdrop-blur',
};

export default function Badge({ type }) {
  if (!type) return null;
  return (
    <span className={cn('rounded-full px-3 py-1 text-[11px] font-medium uppercase tracking-[0.14em]', STYLES[type])}>
      {type}
    </span>
  );
}
