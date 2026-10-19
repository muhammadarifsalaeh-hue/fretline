import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import Reveal from '@/components/ui/Reveal';
import SectionHeading from '@/components/ui/SectionHeading';
import CategoryCard from './CategoryCard';

// ตำแหน่งใน bento grid (Desktop): Electric ใหญ่ซ้าย, Bass กว้างล่างขวา
const LAYOUT = {
  electric: 'md:col-span-2 md:row-span-2',
  acoustic: 'md:col-span-1',
  classical: 'md:col-span-1',
  bass: 'md:col-span-2',
};

export default function Categories() {
  return (
    <section id="categories" className="section-y bg-ink">
      <div className="container-x">
        <Reveal>
          <SectionHeading title={t('cat.title')} action={{ label: t('cat.viewAll'), href: '/guitars' }} />
        </Reveal>

        <Reveal delay={100}>
          {/* Mobile: สไลด์แนวนอน | Desktop: bento grid */}
          <div className="-mx-5 flex snap-x snap-mandatory gap-4 overflow-x-auto px-5 pb-2 [scrollbar-width:none] sm:-mx-8 sm:px-8 md:mx-0 md:grid md:h-[580px] md:grid-cols-4 md:grid-rows-2 md:gap-5 md:overflow-visible md:px-0 md:pb-0 [&::-webkit-scrollbar]:hidden">
            {CATEGORIES.map((category) => (
              <CategoryCard
                key={category.id}
                category={category}
                large={category.id === 'electric'}
                className={`h-[360px] w-[78%] shrink-0 snap-start sm:w-[55%] md:h-auto md:w-auto ${LAYOUT[category.id]}`}
              />
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
