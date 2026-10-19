import { cn } from '@/utils/cn';
import AppLink from '@/components/ui/AppLink';

/** ปุ่มไอคอนกลม (ขนาดแตะ 44px) — มี badge ตัวเลขได้ */
export default function IconButton({ label, href, badge = 0, className = '', children, ...props }) {
  const Comp = href ? AppLink : 'button';
  return (
    <Comp
      href={href}
      aria-label={label}
      className={cn(
        'relative inline-flex h-11 w-11 items-center justify-center rounded-full text-bone/85 transition duration-300 hover:bg-white/10 hover:text-bone',
        className,
      )}
      {...props}
    >
      {children}
      {badge > 0 && (
        <span className="absolute right-1 top-1 grid h-4 min-w-4 place-items-center rounded-full bg-gold px-1 font-mono text-[10px] font-medium text-ink">
          {badge}
        </span>
      )}
    </Comp>
  );
}
