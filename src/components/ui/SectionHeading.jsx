import { cn } from '@/utils/cn';
import AppLink from './AppLink';
import { ArrowRightIcon } from './Icons';

/** หัวข้อ section: title (serif) + ลิงก์ด้านขวา (ไม่บังคับ) */
export default function SectionHeading({ title, action, tone = 'dark', className = '', children }) {
  return (
    <div className={cn('mb-10 flex flex-col gap-6 md:mb-14 md:flex-row md:items-end md:justify-between', className)}>
      <div className="max-w-2xl">
        <h2 className="font-sans text-3xl font-medium leading-[1.1] tracking-tight md:text-4xl lg:text-5xl">{title}</h2>
        {children}
      </div>
      {action && (
        <AppLink
          href={action.href}
          className={cn(
            'group inline-flex min-h-11 items-center gap-2 text-sm transition-colors',
            tone === 'light' ? 'text-ink/70 hover:text-ink' : 'text-bone/70 hover:text-gold',
          )}
        >
          {action.label}
          <ArrowRightIcon size={16} className="transition-transform duration-300 ease-premium group-hover:translate-x-1" />
        </AppLink>
      )}
    </div>
  );
}
