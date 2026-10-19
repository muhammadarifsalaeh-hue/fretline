import { t } from '@/i18n';
import { NOT_SPECIFIED, formatInch, formatKg, formatPrice } from '@/utils/format';

const val = (v) => v ?? NOT_SPECIFIED;

const GROUPS = [
  {
    title: t('group.construction'),
    rows: [
      [t('row.body'), (g) => val(g.specs.body)],
      [t('row.neck'), (g) => val(g.specs.neck)],
      [t('row.fingerboard'), (g) => val(g.specs.fretboard)],
      [t('row.scale'), (g) => formatInch(g.specs.scale)],
      [t('row.frets'), (g) => val(g.specs.frets)],
      [t('row.strings'), (g) => val(g.specs.strings)],
    ],
  },
  {
    title: t('group.electronics'),
    rows: [
      [t('row.pickups'), (g) => val(g.specs.pickups)],
      [t('row.bridge'), (g) => val(g.specs.bridge)],
      [t('row.controls'), (g) => val(g.specs.controls)],
    ],
  },
  {
    title: t('group.details'),
    rows: [
      [t('row.weight'), (g) => formatKg(g.specs.weightKg)],
      [
        t('detail.colors'),
        (g) =>
          g.colors.length === 0 ? (
            NOT_SPECIFIED
          ) : (
          <ul className="flex flex-wrap gap-x-5 gap-y-2">
            {g.colors.map((c) => (
              <li key={c.name} className="flex items-center gap-2">
                <span
                  className={`h-4 w-4 rounded-full ring-1 ring-inset ring-white/25 ${c.hex ? '' : 'bg-gradient-to-br from-white/25 to-white/5'}`}
                  style={c.hex ? { background: c.hex } : undefined}
                />
                {c.name}
              </li>
            ))}
          </ul>
        ),
      ],
      [t('row.price'), (g) => formatPrice(g.price)],
    ],
  },
];

/** ตารางสเปกแบ่งกลุ่ม: หัวข้อซ้าย / รายการขวา */
export default function SpecTable({ guitar }) {
  return (
    <div className="divide-y divide-line border-y border-line">
      {GROUPS.map((group) => (
        <div key={group.title} className="grid gap-4 py-10 lg:grid-cols-12 lg:gap-10">
          <h3 className="font-serif text-3xl leading-tight lg:col-span-4">{group.title}</h3>
          <dl className="lg:col-span-8">
            {group.rows.map(([label, get]) => (
              <div key={label} className="grid grid-cols-[120px_1fr] gap-4 border-b border-line/60 py-4 text-sm last:border-b-0 sm:grid-cols-[180px_1fr]">
                <dt className="text-mute">{label}</dt>
                <dd className="font-mono text-[13px] leading-relaxed text-bone/90">{get(guitar)}</dd>
              </div>
            ))}
          </dl>
        </div>
      ))}
    </div>
  );
}
