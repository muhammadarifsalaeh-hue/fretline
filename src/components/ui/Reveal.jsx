import useInView from '@/hooks/useInView';
import { cn } from '@/utils/cn';

/** ห่อ element ให้ fade + เลื่อนขึ้นเบา ๆ ตอนเลื่อนเข้าจอ (delay เป็น ms สำหรับ stagger) */
export default function Reveal({ as: Tag = 'div', delay = 0, className = '', children }) {
  const [ref, inView] = useInView();
  return (
    <Tag
      ref={ref}
      style={delay ? { transitionDelay: `${delay}ms` } : undefined}
      className={cn('reveal', inView && 'is-visible', className)}
    >
      {children}
    </Tag>
  );
}
