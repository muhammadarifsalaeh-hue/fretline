import { useId } from 'react';
import { t } from '@/i18n';
import { ChevronDownIcon } from './Icons';

export default function SortSelect({ value, onChange, options, label = t('p5.sort') }) {
  const id = useId();
  return (
    <div className="phase5-sort">
      <label htmlFor={id}>{label}</label>
      <div className="relative min-w-0">
        <select id={id} value={value} onChange={(event) => onChange(event.target.value)} className="phase5-select">
          {options.map((option) => <option key={option.id} value={option.id}>{option.label}</option>)}
        </select>
        <ChevronDownIcon size={15} className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-mute" />
      </div>
    </div>
  );
}
