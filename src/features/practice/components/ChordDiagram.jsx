import { useId } from 'react';

const STRINGS = ['E', 'A', 'D', 'G', 'B', 'e'];

/** Front view: low E/string 6 is left, high E/string 1 is right. */
export default function ChordDiagram({ chord, compact = false, className = '' }) {
  const titleId = useId();
  const description = chord.frets.map((fret, index) => `${6 - index}: ${fret === null ? 'mute' : fret === 0 ? 'open' : `fret ${fret}, finger ${chord.fingers[index]}`}`).join('; ');
  return (
    <svg className={`practice-chord-diagram ${className}`} viewBox="0 0 140 180" width="140" height="180"
      role={compact ? undefined : 'img'} aria-hidden={compact ? 'true' : undefined}
      aria-labelledby={compact ? undefined : titleId} data-chord-diagram={chord.id}>
      {!compact && <title id={titleId}>{chord.fullName ?? `${chord.name} ${chord.quality}`}. Strings 6 to 1: {description}</title>}
      <g fill="none" stroke="currentColor">
        {Array.from({ length: 6 }, (_, index) => <line key={`string-${index}`} x1={25 + index * 18} y1="37" x2={25 + index * 18} y2="147" strokeWidth={index < 3 ? 1.3 : .9} opacity=".65" />)}
        {Array.from({ length: 6 }, (_, fret) => <line key={`fret-${fret}`} x1="25" y1={37 + fret * 22} x2="115" y2={37 + fret * 22} strokeWidth={fret === 0 ? 4 : 1} opacity={fret === 0 ? .9 : .5} />)}
      </g>
      {chord.frets.map((fret, index) => (
        <g key={index}>
          {fret === null && <text x={25 + index * 18} y="23" textAnchor="middle" className="practice-diagram-open">×</text>}
          {fret === 0 && <circle cx={25 + index * 18} cy="18" r="4" fill="none" stroke="currentColor" strokeWidth="1.4" />}
          {fret > 0 && <>
            <circle cx={25 + index * 18} cy={26 + fret * 22} r="7.8" className="practice-diagram-dot" />
            <text x={25 + index * 18} y={26 + fret * 22} textAnchor="middle" dominantBaseline="central" className="practice-diagram-finger">{chord.fingers[index]}</text>
          </>}
          <text x={25 + index * 18} y="168" textAnchor="middle" className="practice-diagram-string">{STRINGS[index]}</text>
        </g>
      ))}
      {!compact && Array.from({ length: 5 }, (_, fret) => <text key={fret} x="9" y={48 + fret * 22} textAnchor="middle" dominantBaseline="central" className="practice-diagram-fret">{fret + 1}</text>)}
    </svg>
  );
}
