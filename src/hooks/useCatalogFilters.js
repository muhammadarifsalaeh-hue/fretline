import { t } from '@/i18n';
import { useCallback, useEffect, useMemo, useRef } from 'react';
import { useSearchParams } from 'react-router-dom';
import { GUITARS } from '@/data/guitars';
import { priceCmp } from '@/utils/guitarSort';
import { matchesQuery } from '@/utils/search';

/**
 * State ของ filter/sort/search ทั้งหมดเก็บใน URL (?q=&type=&brand=&min=&max=&sort=)
 * → กด Back ได้, แชร์ลิงก์ได้, และลิงก์จากหน้าอื่น (เช่น หมวดหมู่ / แบรนด์) ใช้ต่อได้ทันที
 */
export const PRICE_STEP = 1000;
export const PRICE_MIN = 0;
const knownPrices = GUITARS.map((g) => g.price).filter((price) => Number.isFinite(price) && price > 0);
export const HAS_CATALOG_PRICES = knownPrices.length > 0;
// Known catalog prices inform presentation, never the meaning of a requested
// budget. An absent maximum is genuinely unbounded, not the current top price.
export const KNOWN_PRICE_MAX = HAS_CATALOG_PRICES ? Math.ceil(Math.max(...knownPrices) / PRICE_STEP) * PRICE_STEP : 0;
export const PRICE_MAX = Number.POSITIVE_INFINITY;

export const SORT_OPTIONS = [
  { id: 'featured', label: t('sort.featured') },
  { id: 'price-asc', label: t('sort.priceAsc') },
  { id: 'price-desc', label: t('sort.priceDesc') },
  { id: 'name', label: t('sort.name') },
];

const SORTERS = {
  featured: (a, b) => Number(b.featured) - Number(a.featured), // sort เสถียร: คงลำดับเดิมในกลุ่มเดียวกัน
  'price-asc': priceCmp(1),
  'price-desc': priceCmp(-1),
  name: (a, b) => `${a.brand} ${a.name}`.localeCompare(`${b.brand} ${b.name}`, undefined, { numeric: true, sensitivity: 'base' }),
};

// แบรนด์ทั้งหมดในแคตตาล็อก เรียงตามจำนวนรุ่น
export const ALL_BRANDS = Object.entries(
  GUITARS.reduce((acc, g) => ({ ...acc, [g.brand]: (acc[g.brand] || 0) + 1 }), {}),
)
  .sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]))
  .map(([name]) => name);

const toList = (value) => [...new Set((value ?? '').split(',').map((item) => item.trim()).filter(Boolean))];
const toggle = (list, value) => (list.includes(value) ? list.filter((x) => x !== value) : [...list, value]);

/** Explicit zero/full-budget filters also exclude models with unknown prices. */
export const hasPriceFilter = (filters) => Boolean(filters.priceActive || filters.min > PRICE_MIN || Number.isFinite(filters.max));

/** กรองกีตาร์ตาม filters; `omit` ใช้ข้ามกลุ่มหนึ่งเพื่อคำนวณจำนวนในแต่ละตัวเลือก */
export function applyFilters(items, f, omit) {
  const priceActive = hasPriceFilter(f);
  return items.filter((g) => {
    if (omit !== 'q' && !matchesQuery(g, f.q)) return false;
    if (omit !== 'types' && f.types.length && !f.types.includes(g.category)) return false;
    if (omit !== 'brands' && f.brands.length && !f.brands.includes(g.brand)) return false;
    // กรองราคาอยู่ → รุ่นที่ไม่มีราคา (Price on request) ถูกซ่อน เพราะยืนยันไม่ได้ว่าอยู่ในช่วง
    if (omit !== 'price' && priceActive && (!Number.isFinite(g.price) || g.price < f.min || g.price > f.max)) return false;
    return true;
  });
}

const countBy = (items, key) => items.reduce((acc, g) => ({ ...acc, [g[key]]: (acc[g[key]] || 0) + 1 }), {});

export function readCatalogFilters(params) {
  const readPrice = (key, fallback) => {
    const value = params.get(key);
    const number = Number(value);
    const explicit = value !== null && value.trim() !== '' && Number.isFinite(number) && Math.abs(number) <= Number.MAX_SAFE_INTEGER;
    return { value: explicit ? Math.max(PRICE_MIN, number) : fallback, explicit };
  };
  const max = readPrice('max', PRICE_MAX);
  const min = readPrice('min', PRICE_MIN);
  const rawPage = Number(params.get('page'));
  const sort = params.get('sort');
  return {
    q: params.get('q') ?? '',
    types: toList(params.get('type')),
    brands: toList(params.get('brand')),
    // Preserve the existing normalization for reversed finite URL bounds.
    min: Math.min(min.value, max.value),
    max: max.value,
    priceActive: min.explicit || max.explicit,
    sort: Object.prototype.hasOwnProperty.call(SORTERS, sort) ? sort : 'featured',
    page: Number.isFinite(rawPage) ? Math.max(1, Math.floor(rawPage)) : 1,
  };
}

/** One serializer preserves URL-owned state across search/facet/history updates. */
export function serializeCatalogFilters(filters) {
  const p = new URLSearchParams();
  if (filters.q.trim()) p.set('q', filters.q);
  if (filters.types.length) p.set('type', filters.types.join(','));
  if (filters.brands.length) p.set('brand', filters.brands.join(','));
  if (hasPriceFilter(filters)) {
    // min=0 preserves an explicitly chosen open-ended budget without adding
    // another query flag. Reset removes both numeric bounds completely.
    if (filters.min > PRICE_MIN || !Number.isFinite(filters.max)) p.set('min', String(filters.min));
    if (Number.isFinite(filters.max)) p.set('max', String(filters.max));
  }
  if (filters.sort !== 'featured') p.set('sort', filters.sort);
  if (filters.page > 1) p.set('page', String(filters.page));
  return p;
}

export default function useCatalogFilters() {
  const [params, setParams] = useSearchParams();
  const filters = useMemo(() => readCatalogFilters(params), [params]);
  const querySession = useRef(null);

  // A typing session uses one history entry. Returning with browser navigation
  // starts a new session instead of overwriting the entry the user returned to.
  useEffect(() => {
    const resetQuerySession = () => { querySession.current = null; };
    window.addEventListener('popstate', resetQuerySession);
    return () => window.removeEventListener('popstate', resetQuerySession);
  }, []);

  const update = useCallback(
    (patch, { replace = false, typing = false } = {}) => {
      const next = { ...filters, page: 1, ...patch };
      const p = serializeCatalogFilters(next);
      const serialized = p.toString();
      if (serialized !== params.toString()) setParams(p, { replace });
      querySession.current = typing ? serialized : null;
    },
    [filters, params, setParams],
  );

  const results = useMemo(() => applyFilters(GUITARS, filters).sort(SORTERS[filters.sort]), [filters]);
  const typeCounts = useMemo(() => countBy(applyFilters(GUITARS, filters, 'types'), 'category'), [filters]);
  const brandCounts = useMemo(() => countBy(applyFilters(GUITARS, filters, 'brands'), 'brand'), [filters]);

  const priceActive = hasPriceFilter(filters);
  const activeCount = filters.types.length + filters.brands.length + (priceActive ? 1 : 0) + (filters.q.trim() ? 1 : 0);

  return {
    filters,
    results,
    typeCounts,
    brandCounts,
    priceActive,
    activeCount,
    setQuery: (q) => update({ q }, { typing: true, replace: querySession.current === params.toString() }),
    setTypes: (types) => update({ types }),
    setSort: (sort) => update({ sort }),
    setPage: (page, replace = false) => update({ page }, { replace }),
    setPrice: (min, max) => update({ min, max, priceActive: true }),
    resetPrice: () => update({ min: PRICE_MIN, max: PRICE_MAX, priceActive: false }),
    toggleType: (id) => update({ types: toggle(filters.types, id) }),
    toggleBrand: (name) => update({ brands: toggle(filters.brands, name) }),
    clearFilters: () => update({ q: '', types: [], brands: [], min: PRICE_MIN, max: PRICE_MAX, priceActive: false }),
  };
}
