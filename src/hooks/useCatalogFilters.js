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
// The fallback is only a URL parsing bound; the price control is hidden when
// there are no source-backed prices. It is never shown as a catalog price range.
export const PRICE_MAX = HAS_CATALOG_PRICES ? Math.ceil(Math.max(...knownPrices) / PRICE_STEP) * PRICE_STEP : 200000;

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
const clampPrice = (n) => Math.min(PRICE_MAX, Math.max(PRICE_MIN, n));
const toggle = (list, value) => (list.includes(value) ? list.filter((x) => x !== value) : [...list, value]);

/** กรองกีตาร์ตาม filters; `omit` ใช้ข้ามกลุ่มหนึ่งเพื่อคำนวณจำนวนในแต่ละตัวเลือก */
export function applyFilters(items, f, omit) {
  return items.filter((g) => {
    if (omit !== 'q' && !matchesQuery(g, f.q)) return false;
    if (omit !== 'types' && f.types.length && !f.types.includes(g.category)) return false;
    if (omit !== 'brands' && f.brands.length && !f.brands.includes(g.brand)) return false;
    // กรองราคาอยู่ → รุ่นที่ไม่มีราคา (Price on request) ถูกซ่อน เพราะยืนยันไม่ได้ว่าอยู่ในช่วง
    const priceActive = f.min > PRICE_MIN || f.max < PRICE_MAX;
    if (omit !== 'price' && priceActive && (g.price == null || g.price < f.min || g.price > f.max)) return false;
    return true;
  });
}

const countBy = (items, key) => items.reduce((acc, g) => ({ ...acc, [g[key]]: (acc[g[key]] || 0) + 1 }), {});

export function readCatalogFilters(params) {
  const readPrice = (key, fallback) => {
    const value = params.get(key);
    return value !== null && value.trim() !== '' && Number.isFinite(Number(value)) ? clampPrice(Number(value)) : fallback;
  };
  const max = readPrice('max', PRICE_MAX);
  const min = readPrice('min', PRICE_MIN);
  const rawPage = Number(params.get('page'));
  const sort = params.get('sort');
  return {
    q: params.get('q') ?? '',
    types: toList(params.get('type')),
    brands: toList(params.get('brand')),
    min: Math.min(min, max),
    max,
    sort: Object.prototype.hasOwnProperty.call(SORTERS, sort) ? sort : 'featured',
    page: Number.isFinite(rawPage) ? Math.max(1, Math.floor(rawPage)) : 1,
  };
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
      const p = new URLSearchParams();
      if (next.q.trim()) p.set('q', next.q);
      if (next.types.length) p.set('type', next.types.join(','));
      if (next.brands.length) p.set('brand', next.brands.join(','));
      if (next.min > PRICE_MIN) p.set('min', String(next.min));
      if (next.max < PRICE_MAX) p.set('max', String(next.max));
      if (next.sort !== 'featured') p.set('sort', next.sort);
      if (next.page > 1) p.set('page', String(next.page));
      const serialized = p.toString();
      if (serialized !== params.toString()) setParams(p, { replace });
      querySession.current = typing ? serialized : null;
    },
    [filters, params, setParams],
  );

  const results = useMemo(() => applyFilters(GUITARS, filters).sort(SORTERS[filters.sort]), [filters]);
  const typeCounts = useMemo(() => countBy(applyFilters(GUITARS, filters, 'types'), 'category'), [filters]);
  const brandCounts = useMemo(() => countBy(applyFilters(GUITARS, filters, 'brands'), 'brand'), [filters]);

  const priceActive = filters.min > PRICE_MIN || filters.max < PRICE_MAX;
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
    setPrice: (min, max) => update({ min, max }),
    resetPrice: () => update({ min: PRICE_MIN, max: PRICE_MAX }),
    toggleType: (id) => update({ types: toggle(filters.types, id) }),
    toggleBrand: (name) => update({ brands: toggle(filters.brands, name) }),
    clearFilters: () => update({ q: '', types: [], brands: [], min: PRICE_MIN, max: PRICE_MAX }),
  };
}
