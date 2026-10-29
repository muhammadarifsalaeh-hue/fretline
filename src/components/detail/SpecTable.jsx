import { t } from '@/i18n';
import { NOT_SPECIFIED, formatScale, formatKg, formatPrice } from '@/utils/format';
import { ADDITIONAL_SPECIFICATIONS } from '@/data/additionalSpecifications';
import PriceSourceNote from '@/components/guitar/PriceSourceNote';

const unknown = (g) => g.intake?.batch === 'yamaha-2026-10-26' ? t('import.unconfirmed') : NOT_SPECIFIED;
const val = (v, g) => v ?? unknown(g);

const GROUPS = [
  {
    id: 'construction',
    title: t('group.construction'),
    rows: [
      [t('row.body'), (g) => val(g.specs.body, g)],
      [t('row.neck'), (g) => val(g.specs.neck, g)],
      [t('row.fingerboard'), (g) => val(g.specs.fretboard, g)],
      [t('row.scale'), (g) => formatScale(g.specs)],
      [t('row.frets'), (g) => val(g.specs.frets, g)],
      [t('row.strings'), (g) => val(g.specs.strings, g)],
    ],
  },
  {
    id: 'electronics',
    title: t('group.electronics'),
    rows: [
      [t('row.pickups'), (g) => val(g.specs.pickups, g)],
      [t('row.bridge'), (g) => val(g.specs.bridge, g)],
      [t('row.controls'), (g) => val(g.specs.controls, g)],
    ],
  },
  {
    id: 'details',
    title: t('group.details'),
    rows: [
      [t('row.weight'), (g) => g.specs.weightKg == null ? unknown(g) : formatKg(g.specs.weightKg)],
      [
        t('detail.colors'),
        (g) =>
          g.colors.length === 0 ? (
            unknown(g)
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
      [t('row.price'), (g) => <>{formatPrice(g.price)}<PriceSourceNote guitar={g} /></>],
    ],
  },
];

/** ตารางสเปกแบ่งกลุ่ม: หัวข้อซ้าย / รายการขวา */
export default function SpecTable({ guitar }) {
  return (
    <table className="spec-table w-full text-left">
      <caption className="sr-only">{t('detail.specs')} — {guitar.brand} {guitar.name}</caption>
      {GROUPS.map((group) => (
        <tbody key={group.title}>
          <tr><th colSpan={2} scope="colgroup" className="spec-group">{group.title}</th></tr>
          {[...group.rows, ...ADDITIONAL_SPECIFICATIONS.filter((field) => field.group === group.id && Object.hasOwn(guitar.specs, field.key))
            .map((field) => [t(field.label), (g) => g.specs[field.key] == null ? unknown(g) : `${g.specs[field.key]}${field.unit ?? ''}`])].map(([label, get]) => (
            <tr key={label}>
              <th scope="row">{label}</th>
              <td>{get(guitar)}</td>
            </tr>
          ))}
        </tbody>
      ))}
    </table>
  );
}
