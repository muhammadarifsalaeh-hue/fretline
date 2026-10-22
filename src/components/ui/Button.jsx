import { cn } from '@/utils/cn';
import AppLink from './AppLink';

const VARIANTS = {
  primary: 'bg-gold text-ink hover:bg-gold-soft',
  ghost: 'border border-white/20 text-bone hover:border-gold hover:text-gold',
  dark: 'bg-ink text-bone hover:bg-surface-2',
  light: 'bg-bone text-ink hover:bg-white',
};
const SIZES = {
  md: 'h-12 px-7 text-sm',
  lg: 'h-14 px-9 text-[15px]',
};

/** ปุ่ม pill — ถ้าใส่ href จะเป็น <a>, ไม่ใส่จะเป็น <button> */
export default function Button({ href, variant = 'primary', size = 'md', className = '', children, ...props }) {
  const Comp = href ? AppLink : 'button';
  return (
    <Comp
      href={href}
      type={href ? undefined : 'button'}
      className={cn(
        'fl-button inline-flex items-center justify-center gap-2 font-medium disabled:cursor-not-allowed disabled:opacity-50',
        VARIANTS[variant],
        SIZES[size],
        className,
      )}
      {...props}
    >
      {children}
    </Comp>
  );
}
