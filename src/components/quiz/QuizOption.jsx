import { cn } from '@/utils/cn';
import { useId } from 'react';
import { CheckIcon, GuitarIcon } from '@/components/ui/Icons';
import GuitarArt from '@/components/ui/GuitarArt';

export default function QuizOption({ name, option, checked, onSelect }) {
  const id = useId();
  const illustrated = name === 'type' && option.value !== 'any';
  return (
    <label className={cn('quiz-option', checked && 'is-selected', name === 'type' && option.value === 'any' && 'quiz-any-option')}>
      <input type="radio" name={name} value={option.value} checked={checked} aria-labelledby={`${id}-title`} aria-describedby={`${id}-description`} onChange={() => onSelect(option.value)} className="peer sr-only" />
      <span className="pointer-events-none absolute inset-0 rounded-xl peer-focus-visible:outline peer-focus-visible:outline-2 peer-focus-visible:outline-offset-2 peer-focus-visible:outline-gold" aria-hidden="true" />
      {illustrated && <div className="quiz-option-art" aria-hidden="true"><GuitarArt type={option.value} className="h-full w-auto -rotate-6 text-gold/80" /></div>}
      <span className="flex items-start justify-between gap-3"><span id={`${id}-title`} className="quiz-option-title">{name === 'type' && option.value === 'any' && <GuitarIcon size={18} className="mr-2 inline text-gold" />}{option.label}</span><span className="quiz-option-check" aria-hidden="true">{checked && <CheckIcon size={13} />}</span></span>
      <span id={`${id}-description`} className="mt-2 block text-xs leading-6 text-mute">{option.desc}</span>
    </label>
  );
}
