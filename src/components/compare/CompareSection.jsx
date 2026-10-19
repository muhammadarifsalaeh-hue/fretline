import { t } from '@/i18n';
import { useState } from 'react';
import { GUITARS_BY_ID } from '@/data/guitars';
import { useShop } from '@/context/ShopContext';
import Button from '@/components/ui/Button';
import { CheckIcon } from '@/components/ui/Icons';
import Reveal from '@/components/ui/Reveal';
import Switch from '@/components/ui/Switch';
import CompareTable from './CompareTable';

// ตัวอย่างที่แสดงเมื่อผู้ใช้ยังไม่ได้เลือกกีตาร์เปรียบเทียบ
const SAMPLE_IDS = ['fender-american-professional-ii-stratocaster', 'gibson-les-paul-standard-60s'];

const BENEFITS = [
  t('cmpsec.b1'),
  t('cmpsec.b2'),
  t('cmpsec.b3'),
];

export default function CompareSection() {
  const { compare, removeCompare } = useShop();
  const [diffOnly, setDiffOnly] = useState(true);

  const selected = compare.map((id) => GUITARS_BY_ID[id]).filter(Boolean);
  const usingSelection = selected.length >= 2;
  const guitars = usingSelection ? selected : SAMPLE_IDS.map((id) => GUITARS_BY_ID[id]);

  return (
    <section id="compare" className="section-y bg-surface">
      <div className="container-x grid gap-12 lg:grid-cols-12 lg:items-center lg:gap-16">
        <Reveal className="lg:col-span-5">
          <h2 className="font-sans text-3xl font-medium leading-[1.15] tracking-tight md:text-4xl lg:text-5xl">
            {t('cmpsec.title')}
          </h2>
          <ul className="mt-8 space-y-4">
            {BENEFITS.map((text) => (
              <li key={text} className="flex items-start gap-3 text-bone/80">
                <span className="mt-0.5 grid h-6 w-6 shrink-0 place-items-center rounded-full border border-gold/50 text-gold">
                  <CheckIcon size={14} />
                </span>
                {text}
              </li>
            ))}
          </ul>
          <Button href="/compare" size="lg" className="mt-10 w-full sm:w-auto">
            {usingSelection ? t('cmpsec.open') : t('cmpsec.start')}
          </Button>
          <p className="mt-4 max-w-sm text-sm text-mute">
            {usingSelection
              ? t('cmpsec.noteSelected')
              : t('cmpsec.noteSample')}
          </p>
        </Reveal>

        <Reveal delay={120} className="min-w-0 lg:col-span-7">
          <div className="rounded-3xl border border-line bg-ink p-4 sm:p-6 md:p-8">
            <div className="mb-6 flex items-center justify-between gap-4">
              <p className="text-sm text-mute">{usingSelection ? t('cmpsec.yours') : t('cmpsec.sample')}</p>
              <Switch checked={diffOnly} onChange={setDiffOnly} label={t('cmp.diffOnly')} />
            </div>

            <CompareTable
              guitars={guitars}
              diffOnly={diffOnly}
              onRemove={usingSelection ? removeCompare : undefined}
            />
          </div>
        </Reveal>
      </div>
    </section>
  );
}
