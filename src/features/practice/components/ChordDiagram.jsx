import { useId } from 'react';

const STRINGS = ['E', 'A', 'D', 'G', 'B', 'e'];
const stringX = (index) => 28 + index * 18;

// A barre can pass behind a higher finger, but must never cross an open/muted string.
function barreSegments(chord, barre) {
  const first = 6 - Math.max(barre.fromString, barre.toString);
  const last = 6 - Math.min(barre.fromString, barre.toString);
  const segments = [];
  let start = null;
  for (let index = first; index <= last + 1; index += 1) {
    const covered = index <= last && chord.frets[index] !== null && chord.frets[index] >= barre.fret;
    if (covered && start === null) start = index;
    if (!covered && start !== null) {
      segments.push([start, index - 1]);
      start = null;
    }
  }
  return segments;
}

/** Front view: string 6 / low E is left; string 1 / high E is right. */
export default function ChordDiagram({ chord, compact = false, className = '' }) {
  const titleId = useId();
  const baseFret = chord.baseFret ?? 1;
  const fretCount = Math.max(5, ...chord.frets.filter((fret) => fret > 0).map((fret) => fret - baseFret + 1));
  const fretY = (fret) => 37 + (fret - baseFret + 0.5) * 22;
  const bottom = 37 + fretCount * 22;
  const barres = chord.barres ?? [];
  const description = chord.frets.map((fret, index) => (6 - index) + ': ' + (fret === null ? 'mute' : fret === 0 ? 'open' : 'fret ' + fret + ', finger ' + chord.fingers[index]) + (chord.notes?.[index] ? ', ' + chord.notes[index] : '')).join('; ');

  return (
    <svg className={'practice-chord-diagram ' + className} viewBox={'0 0 148 ' + (bottom + 33)} width="148" height={bottom + 33}
      role={compact ? undefined : 'img'} aria-hidden={compact ? 'true' : undefined}
      aria-labelledby={compact ? undefined : titleId} data-chord-diagram={chord.id} data-base-fret={baseFret} data-string-order="6,5,4,3,2,1">
      {!compact && <title id={titleId}>{chord.fullName ?? chord.name}. Strings 6 to 1: {description}. {barres.map((barre) => 'Finger ' + barre.finger + ' barre at fret ' + barre.fret + ', strings ' + barre.fromString + ' to ' + barre.toString).join('; ')}</title>}
      <g fill="none" stroke="currentColor">
        {Array.from({ length: 6 }, (_, index) => <line key={'string-' + index} x1={stringX(index)} y1="37" x2={stringX(index)} y2={bottom} strokeWidth={index < 3 ? 1.3 : 0.9} opacity=".65" />)}
        {Array.from({ length: fretCount + 1 }, (_, fret) => <line key={'fret-' + fret} x1="28" y1={37 + fret * 22} x2="118" y2={37 + fret * 22}
          data-fret-boundary={baseFret + fret - 1} data-nut={fret === 0 && baseFret === 1 ? 'true' : undefined}
          strokeWidth={fret === 0 && baseFret === 1 ? 4 : 1} opacity={fret === 0 && baseFret === 1 ? 0.9 : 0.5} />)}
      </g>
      <g className="practice-diagram-barres">
        {barres.map((barre, index) => <g key={index} data-chord-barre={index} data-finger={barre.finger} data-fret={barre.fret} data-from-string={barre.fromString} data-to-string={barre.toString}>
          {barreSegments(chord, barre).map(([first, last]) => <line key={first} x1={stringX(first)} y1={fretY(barre.fret)} x2={stringX(last)} y2={fretY(barre.fret)} strokeWidth="13" strokeLinecap="round" />)}
        </g>)}
      </g>
      {chord.frets.map((fret, index) => (
        <g key={index} data-chord-string={6 - index} data-string={6 - index} data-fret={fret === null ? 'mute' : fret}
          data-finger={chord.fingers[index] ?? ''} data-note={chord.notes?.[index] ?? ''} data-string-state={fret === null ? 'muted' : fret === 0 ? 'open' : 'fretted'}>
          {fret === null && <text x={stringX(index)} y="23" textAnchor="middle" className="practice-diagram-open">×</text>}
          {fret === 0 && <circle cx={stringX(index)} cy="18" r="4" fill="none" stroke="currentColor" strokeWidth="1.4" />}
          {fret > 0 && <>
            <circle cx={stringX(index)} cy={fretY(fret)} r="7.8" className="practice-diagram-dot" />
            <text x={stringX(index)} y={fretY(fret)} textAnchor="middle" dominantBaseline="central" className="practice-diagram-finger">{chord.fingers[index]}</text>
          </>}
          <text x={stringX(index)} y={bottom + 21} textAnchor="middle" className="practice-diagram-string">{STRINGS[index]}</text>
        </g>
      ))}
      {Array.from({ length: fretCount }, (_, fret) => (!compact || (fret === 0 && baseFret > 1)) && <text key={fret} x="11" y={fretY(baseFret + fret)} textAnchor="middle" dominantBaseline="central" className="practice-diagram-fret" data-fret-label={baseFret + fret}>{baseFret + fret}</text>)}
    </svg>
  );
}
