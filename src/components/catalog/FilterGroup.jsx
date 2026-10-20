import { useId, useState } from 'react';
import { cn } from '@/utils/cn';
import { ChevronDownIcon } from '@/components/ui/Icons';

/** กลุ่ม filter ที่พับ/ขยายได้ (animation เลื่อนความสูงแบบ grid-rows) */
export default function FilterGroup({ title, defaultOpen = true, children }) {
  const [open, setOpen] = useState(defaultOpen);
  const id = useId();
  return (
    <section className="border-b border-line py-5 first:pt-0 last:border-b-0">
      <h3>
        <button
          type="button"
          aria-expanded={open}
          aria-controls={id}
          onClick={() => setOpen(!open)}
          className="flex min-h-11 w-full items-center justify-between text-left text-sm font-medium text-bone"
        >
          {title}
          <ChevronDownIcon size={18} className={cn('text-mute transition-transform duration-300', open && 'rotate-180')} />
        </button>
      </h3>
      <div
        id={id}
        inert={!open ? '' : undefined}
        className={cn(
          'grid transition-[grid-template-rows,opacity] duration-500 ease-premium',
          open ? 'grid-rows-[1fr] opacity-100' : 'grid-rows-[0fr] opacity-0',
        )}
      >
        <div className="-mx-1 min-h-0 overflow-y-clip px-1">
          <div className="pt-2">{children}</div>
        </div>
      </div>
    </section>
  );
}
