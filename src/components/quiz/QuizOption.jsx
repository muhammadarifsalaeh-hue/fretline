import { cn } from '@/utils/cn';
import { useId } from 'react';
import { CheckIcon } from '@/components/ui/Icons';
import { QuizGlyph } from './QuizVisuals';

export default function QuizOption({ name, option, checked, onSelect, supplemental = false }) {
  const id = useId();
  return <label className={cn('quiz-option', checked && 'is-selected', supplemental && 'quiz-supplemental-option', name === 'type' && option.value === 'any' && 'quiz-any-option')}>
    <input type="radio" name={name} value={option.value} checked={checked} aria-labelledby={`${id}-title`} aria-describedby={`${id}-description`} onChange={() => onSelect(option.value)} className="peer sr-only" />
    <span className="quiz-option-focus" aria-hidden="true" />
    <span className="quiz-option-symbol" aria-hidden="true"><QuizGlyph kind={name} size={26} /></span>
    <span className="quiz-option-copy"><span id={`${id}-title`} className="quiz-option-title">{option.label}</span><span id={`${id}-description`} className="quiz-option-description">{option.desc}</span></span>
    <span className="quiz-option-check" aria-hidden="true">{checked && <CheckIcon size={12} />}</span>
  </label>;
}
