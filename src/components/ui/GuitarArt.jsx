/**
 * ภาพเส้นร่าง (line art) ของกีตาร์แต่ละประเภท — ใช้เป็นภาพชั่วคราวแทนรูปถ่ายที่ยังไม่มี
 * เป็นภาพประกอบทั่วไป ไม่ได้แสดงรุ่นหรือยี่ห้อใดโดยเฉพาะ
 * type: electric | acoustic | classical | bass
 */
const STROKE = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.4, strokeLinecap: 'round', strokeLinejoin: 'round', vectorEffect: 'non-scaling-stroke' };

function Strings({ x, y1, y2, count = 6, gap = 2.4 }) {
  const start = x - ((count - 1) * gap) / 2;
  return Array.from({ length: count }, (_, i) => (
    <line key={i} x1={start + i * gap} y1={y1} x2={start + i * gap} y2={y2} {...STROKE} strokeWidth={0.7} opacity={0.7} />
  ));
}

const SHAPES = {
  electric: (
    <>
      {/* หัวกีตาร์ + คอ */}
      <path d="M95 8c-4 0-6 3-6 7v22h12V15c0-4-2-7-6-7z" {...STROKE} />
      <rect x="91" y="37" width="8" height="132" rx="1.5" {...STROKE} />
      {[52, 66, 79, 91, 102, 112, 121, 130, 138, 146, 153, 159].map((y) => (
        <line key={y} x1="91" y1={y} x2="99" y2={y} {...STROKE} strokeWidth={0.6} opacity={0.6} />
      ))}
      {/* บอดี้ ทรง double-cutaway */}
      <path
        d="M95 160c-10-9-22-6-26-17-3-9 2-16-2-24-4-8-13-10-13-24 0-12 9-17 15-15 8 3 9 12 14 14 5 2 8-3 12-3s7 5 12 3c5-2 6-11 14-14 6-2 15 3 15 15 0 14-9 16-13 24-4 8 1 15-2 24-4 11-16 8-26 17z"
        transform="translate(0 52)"
        {...STROKE}
      />
      {/* ปิ๊กอัพ + บริดจ์ */}
      <rect x="86" y="188" width="18" height="6" rx="1.5" {...STROKE} />
      <rect x="86" y="201" width="18" height="6" rx="1.5" {...STROKE} />
      <rect x="86" y="214" width="18" height="6" rx="1.5" {...STROKE} />
      <rect x="84" y="228" width="22" height="5" rx="1.5" {...STROKE} />
      <circle cx="112" cy="238" r="2.2" {...STROKE} />
      <circle cx="118" cy="231" r="2.2" {...STROKE} />
      <Strings x={95} y1={30} y2={230} />
    </>
  ),
  acoustic: (
    <>
      <path d="M95 8c-4 0-6 3-6 7v22h12V15c0-4-2-7-6-7z" {...STROKE} />
      <rect x="91" y="37" width="8" height="112" rx="1.5" {...STROKE} />
      {[50, 63, 75, 86, 96, 105, 114, 122, 129, 136].map((y) => (
        <line key={y} x1="91" y1={y} x2="99" y2={y} {...STROKE} strokeWidth={0.6} opacity={0.6} />
      ))}
      {/* บอดี้ ทรง dreadnought */}
      <path
        d="M95 140c-12 0-20 6-21 15-1 9 6 12 6 20 0 7-14 12-14 33 0 18 14 30 29 30s29-12 29-30c0-21-14-26-14-33 0-8 7-11 6-20-1-9-9-15-21-15z"
        transform="translate(0 -4)"
        {...STROKE}
      />
      <circle cx="95" cy="178" r="11" {...STROKE} />
      <circle cx="95" cy="178" r="13.5" {...STROKE} strokeWidth={0.7} opacity={0.6} />
      <rect x="84" y="222" width="22" height="4" rx="1.5" {...STROKE} />
      <Strings x={95} y1={30} y2={222} />
    </>
  ),
  classical: (
    <>
      {/* หัวแบบ slotted และคอกว้าง */}
      <rect x="86" y="6" width="18" height="34" rx="3" {...STROKE} />
      <line x1="90" y1="14" x2="90" y2="30" {...STROKE} strokeWidth={0.8} opacity={0.6} />
      <line x1="100" y1="14" x2="100" y2="30" {...STROKE} strokeWidth={0.8} opacity={0.6} />
      <rect x="89" y="40" width="12" height="108" rx="1.5" {...STROKE} />
      {[52, 64, 76, 87, 97, 106, 114, 122, 129].map((y) => (
        <line key={y} x1="89" y1={y} x2="101" y2={y} {...STROKE} strokeWidth={0.6} opacity={0.6} />
      ))}
      <path
        d="M95 140c-13 0-22 6-23 15-1 8 5 11 5 19 0 8-15 13-15 34 0 18 15 30 33 30s33-12 33-30c0-21-15-26-15-34 0-8 6-11 5-19-1-9-10-15-23-15z"
        transform="translate(0 -4)"
        {...STROKE}
      />
      <circle cx="95" cy="178" r="11" {...STROKE} />
      <rect x="82" y="224" width="26" height="4" rx="1.5" {...STROKE} />
      <Strings x={95} y1={34} y2={224} gap={1.9} />
    </>
  ),
  bass: (
    <>
      <path d="M95 6c-4 0-6 3-6 7v28h12V13c0-4-2-7-6-7z" {...STROKE} />
      <rect x="91" y="41" width="8" height="150" rx="1.5" {...STROKE} />
      {[56, 72, 87, 101, 114, 126, 137, 147, 156, 164, 171].map((y) => (
        <line key={y} x1="91" y1={y} x2="99" y2={y} {...STROKE} strokeWidth={0.6} opacity={0.6} />
      ))}
      <path
        d="M95 168c-10-8-20-5-24-15-3-8 2-14-1-21-4-8-12-9-12-21 0-11 8-15 14-13 7 3 8 11 13 13 4 1 7-3 10-3s6 4 10 3c5-2 6-10 13-13 6-2 14 2 14 13 0 12-8 13-12 21-3 7 2 13-1 21-4 10-14 7-24 15z"
        transform="translate(0 56)"
        {...STROKE}
      />
      <rect x="86" y="206" width="18" height="7" rx="1.5" {...STROKE} />
      <rect x="86" y="219" width="18" height="7" rx="1.5" {...STROKE} />
      <rect x="82" y="232" width="26" height="5" rx="1.5" {...STROKE} />
      <Strings x={95} y1={34} y2={234} count={4} gap={3} />
    </>
  ),
};

export default function GuitarArt({ type = 'electric', className = '', ...props }) {
  return (
    <svg viewBox="0 0 190 250" aria-hidden="true" focusable="false" className={className} {...props}>
      {SHAPES[type] ?? SHAPES.electric}
    </svg>
  );
}
