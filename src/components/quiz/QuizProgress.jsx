import { cn } from '@/utils/cn';
import { ChevronLeftIcon } from '@/components/ui/Icons';

/** แถบความคืบหน้า + ปุ่มย้อนกลับ */
export default function QuizProgress({ index, total, onBack }) {
  return (
    <div className="mb-10 md:mb-14">
      <div className="mb-4 flex items-center justify-between">
        <button
          type="button"
          onClick={onBack}
          className="-ml-2 inline-flex min-h-[44px] items-center gap-1 px-2 text-sm text-bone/70 transition-colors hover:text-bone"
        >
          <ChevronLeftIcon size={18} />
          Back
        </button>
        <p className="font-mono text-sm text-mute" aria-live="polite">
          Question {index + 1} of {total}
        </p>
      </div>
      <div className="flex gap-2" role="progressbar" aria-valuemin={1} aria-valuemax={total} aria-valuenow={index + 1}>
        {Array.from({ length: total }, (_, i) => (
          <span key={i} className="h-0.5 flex-1 overflow-hidden rounded-full bg-line">
            <span className={cn('block h-full bg-gold transition-[width] duration-700 ease-premium', i <= index ? 'w-full' : 'w-0')} />
          </span>
        ))}
      </div>
    </div>
  );
}
