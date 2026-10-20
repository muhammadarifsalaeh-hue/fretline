import { useId, useLayoutEffect, useRef, useState } from 'react';
import { cn } from '@/utils/cn';

/** แท็บที่มีเส้นใต้เลื่อนตามแท็บที่เลือก */
export default function Tabs({ tabs, value, onChange, tone = 'dark', label, panelId, idPrefix }) {
  const refs = useRef({});
  const generatedId = useId();
  const prefix = idPrefix ?? generatedId;
  const [bar, setBar] = useState({ left: 0, width: 0 });

  useLayoutEffect(() => {
    const measure = () => {
      const el = refs.current[value];
      if (el) setBar({ left: el.offsetLeft, width: el.offsetWidth });
    };
    measure();
    window.addEventListener('resize', measure);
    return () => window.removeEventListener('resize', measure);
  }, [value, tabs]);

  const light = tone === 'light';

  return (
    <div role="tablist" aria-label={label} className={cn('featured-tabs relative flex gap-7 border-b', light ? 'border-ink/10' : 'border-line')}>
      {tabs.map((tab) => (
        <button
          key={tab.id}
          ref={(el) => {
            refs.current[tab.id] = el;
          }}
          role="tab"
          id={`${prefix}-${tab.id}`}
          type="button"
          tabIndex={value === tab.id ? 0 : -1}
          aria-selected={value === tab.id}
          aria-controls={panelId}
          onKeyDown={(event) => {
            const index = tabs.findIndex((item) => item.id === tab.id);
            const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1
              : event.key === 'ArrowRight' ? (index + 1) % tabs.length
                : event.key === 'ArrowLeft' ? (index - 1 + tabs.length) % tabs.length : null;
            if (next === null) return;
            event.preventDefault();
            onChange(tabs[next].id);
            refs.current[tabs[next].id]?.focus();
          }}
          onClick={() => onChange(tab.id)}
          className={cn(
            'min-h-[44px] pb-3 pt-2 text-sm transition-colors duration-300',
            value === tab.id
              ? light ? 'text-ink' : 'text-bone'
              : light ? 'text-ink/45 hover:text-ink' : 'text-mute hover:text-bone',
          )}
        >
          {tab.label}
        </button>
      ))}
      <span
        aria-hidden="true"
        className={cn('absolute -bottom-px left-0 h-0.5 transition-[transform,width] duration-500 ease-premium', light ? 'bg-ink' : 'bg-gold')}
        style={{ transform: `translateX(${bar.left}px)`, width: bar.width }}
      />
    </div>
  );
}
