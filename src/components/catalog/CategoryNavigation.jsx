import { CATEGORIES } from '@/data/categories';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import GuitarArt from '@/components/ui/GuitarArt';
import { GridIcon } from '@/components/ui/Icons';

const THAI_GUITAR_PREFIX = 'กีตาร์';

export default function CategoryNavigation({ types, onSelect }) {
  const categories = [{ id: 'all', name: t('common.all') }, ...CATEGORIES];
  return (
    <nav aria-label={t('catalog.categories')} className="catalog-categories">
      {categories.map((category) => {
        const active = category.id === 'all' ? types.length === 0 : types.includes(category.id);
        return (
          <button key={category.id} type="button" aria-pressed={active}
            onClick={() => onSelect(category.id)}
            className={cn('category-navigation-item', active && 'is-active')}>
            {category.id === 'all' ? <GridIcon size={24} /> : <GuitarArt type={category.id} className="h-8 w-7 -rotate-12" />}
            <span className="category-navigation-label">
              {category.name.startsWith(THAI_GUITAR_PREFIX) ? (
                <>
                  <span className="inline-block whitespace-nowrap">{THAI_GUITAR_PREFIX}</span><wbr />
                  <span className="inline-block whitespace-nowrap">{category.name.slice(THAI_GUITAR_PREFIX.length)}</span>
                </>
              ) : category.name}
            </span>
          </button>
        );
      })}
    </nav>
  );
}
