import { t } from '@/i18n';
import { useState } from 'react';
import { CATEGORIES } from '@/data/categories';
import { ALL_BRANDS } from '@/hooks/useCatalogFilters';
import FilterCheckbox from './FilterCheckbox';
import FilterGroup from './FilterGroup';
import PriceRange from './PriceRange';

const BRANDS_COLLAPSED = 6;

/** เนื้อหา filter ทั้งหมด — ใช้ทั้งใน sidebar (Desktop) และ drawer (Mobile) */
export default function FilterPanel({ filters, typeCounts, brandCounts, onToggleType, onToggleBrand, onPrice }) {
  const [showAll, setShowAll] = useState(false);

  // ตอนพับ: แสดงแบรนด์ยอดนิยม + แบรนด์ที่ถูกเลือกไว้เสมอ
  const brands = showAll
    ? ALL_BRANDS
    : ALL_BRANDS.filter((b, i) => i < BRANDS_COLLAPSED || filters.brands.includes(b));
  const hiddenCount = ALL_BRANDS.length - brands.length;

  return (
    <div>
      <FilterGroup title={t('filter.type')}>
        {CATEGORIES.map((c) => (
          <FilterCheckbox
            key={c.id}
            label={c.name}
            count={typeCounts[c.id] || 0}
            checked={filters.types.includes(c.id)}
            onChange={() => onToggleType(c.id)}
          />
        ))}
      </FilterGroup>

      <FilterGroup title={t('filter.brand')}>
        {brands.map((b) => (
          <FilterCheckbox
            key={b}
            label={b}
            count={brandCounts[b] || 0}
            checked={filters.brands.includes(b)}
            onChange={() => onToggleBrand(b)}
          />
        ))}
        {(hiddenCount > 0 || showAll) && (
          <button
            type="button"
            onClick={() => setShowAll(!showAll)}
            className="mt-2 min-h-[40px] text-sm text-gold transition-colors hover:text-gold-soft"
          >
            {showAll ? t('filter.showFewer') : t('filter.showMore', { n: hiddenCount })}
          </button>
        )}
      </FilterGroup>

      <FilterGroup title={t('filter.price')}>
        <PriceRange min={filters.min} max={filters.max} onChange={onPrice} />
      </FilterGroup>
    </div>
  );
}
