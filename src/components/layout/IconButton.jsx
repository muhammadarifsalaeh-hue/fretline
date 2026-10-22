import { cn } from '@/utils/cn';
import AppLink from '@/components/ui/AppLink';

/** ปุ่มไอคอนกลม (ขนาดแตะ 44px) — มี badge ตัวเลขได้ */
export default function IconButton({ label, href, badge = 0, className = '', children, ...props }) {
  const Comp = href ? AppLink : 'button';
  return (
    <Comp
      href={href}
      type={href ? undefined : 'button'}
      aria-label={label}
      className={cn(
        'site-icon-button relative inline-flex h-11 w-11 shrink-0 items-center justify-center rounded-lg text-bone/85 transition-colors duration-200 hover:bg-white/5 hover:text-bone motion-reduce:transition-none',
        className,
      )}
      {...props}
    >
      {children}
      {badge > 0 && (
        <span className="site-icon-badge absolute right-0.5 top-0.5 grid h-[18px] min-w-[18px] place-items-center rounded-full bg-gold px-1 text-[11px] font-medium leading-none text-ink">
          {badge}
        </span>
      )}
    </Comp>
  );
}
