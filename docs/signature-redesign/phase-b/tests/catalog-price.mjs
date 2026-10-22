import assert from 'node:assert/strict';
import { createServer as createHttpServer } from 'node:http';
import { fileURLToPath } from 'node:url';
import { renderToStaticMarkup } from 'react-dom/server';
import { createServer } from 'vite';

// Exercise the actual catalog functions and rendered control without adding a
// test dependency or opening a web server. Run from any working directory.
const root = fileURLToPath(new URL('../../../../', import.meta.url));
// Vite 5 creates a websocket listener even with hmr:false in middleware mode.
// Attach HMR to an unlistened HTTP server so these checks never bind a port.
const hmrServer = createHttpServer();
const server = await createServer({ root, server: { middlewareMode: true, hmr: { server: hmrServer } }, appType: 'custom', logLevel: 'error' });
let passed = 0;
const check = (name, test) => { test(); passed++; console.log(`PASS ${name}`); };
const ids = (items) => items.map((guitar) => guitar.id);
const elements = (element) => {
  if (!element || typeof element !== 'object') return [];
  return [element, ...[element.props?.children].flat(Infinity).flatMap(elements)];
};

try {
  const { GUITARS, ARCHIVED_GUITARS } = await server.ssrLoadModule('/src/data/guitars.js');
  const { applyFilters, readCatalogFilters, serializeCatalogFilters, hasPriceFilter, PRICE_MIN, PRICE_MAX, KNOWN_PRICE_MAX, ALL_BRANDS } = await server.ssrLoadModule('/src/hooks/useCatalogFilters.js');
  const { default: PriceRange, getPriceSliderDomain } = await server.ssrLoadModule('/src/components/catalog/PriceRange.jsx');
  const defaults = readCatalogFilters(new URLSearchParams());
  const read = (query) => readCatalogFilters(new URLSearchParams(query));
  const known = GUITARS.filter((guitar) => Number.isFinite(guitar.price));
  const unknown = GUITARS.filter((guitar) => !Number.isFinite(guitar.price));
  const pacifica = GUITARS.find((guitar) => guitar.id === 'yamaha-pacifica-612viifm');

  check('An absent budget retains the full catalog, including unknown prices', () => {
    assert.equal(defaults.min, 0);
    assert.equal(defaults.max, Infinity);
    assert.equal(hasPriceFilter(defaults), false);
    assert.deepEqual(ids(applyFilters(GUITARS, defaults)), ids(GUITARS));
    assert.ok(unknown.length > 0);
  });

  check('The real public price remains 34000 and never becomes a budget ceiling', () => {
    assert.equal(pacifica.price, 34000);
    assert.equal(KNOWN_PRICE_MAX, 34000);
    assert.equal(PRICE_MAX, Infinity);
    assert.equal(read('min=70000').min, 70000);
    assert.deepEqual(applyFilters(GUITARS, read('min=70000')), []);
  });

  check('High bookmarked bounds preserve the requested numbers exactly', () => {
    const filters = read('min=80000&max=235001');
    assert.equal(filters.min, 80000);
    assert.equal(filters.max, 235001);
    assert.equal(serializeCatalogFilters(filters).toString(), 'min=80000&max=235001');
    assert.deepEqual(applyFilters(GUITARS, filters), []);
  });

  check('An explicit high maximum excludes unknowns without clamping its URL', () => {
    const filters = read('max=200000');
    assert.equal(filters.max, 200000);
    assert.deepEqual(ids(applyFilters(GUITARS, filters)), ids(known));
    assert.equal(serializeCatalogFilters(filters).get('max'), '200000');
  });

  check('Price limits are inclusive and preserve exact one-baht boundaries', () => {
    assert.deepEqual(ids(applyFilters(GUITARS, read('min=34000&max=34000'))), [pacifica.id]);
    assert.deepEqual(ids(applyFilters(GUITARS, read('min=34000'))), [pacifica.id]);
    assert.deepEqual(ids(applyFilters(GUITARS, read('max=34000'))), [pacifica.id]);
    assert.deepEqual(applyFilters(GUITARS, read('min=34001')), []);
    assert.deepEqual(applyFilters(GUITARS, read('max=33999')), []);
  });

  check('An explicit zero maximum is a real filter rather than the default', () => {
    const filters = read('max=0');
    assert.equal(hasPriceFilter(filters), true);
    assert.equal(filters.max, 0);
    assert.deepEqual(applyFilters(GUITARS, filters), []);
    assert.equal(serializeCatalogFilters(filters).get('max'), '0');
  });

  check('Explicit min=0 means known prices only and survives URL round trips', () => {
    const filters = read('min=0');
    assert.equal(hasPriceFilter(filters), true);
    assert.deepEqual(ids(applyFilters(GUITARS, filters)), ids(known));
    const serialized = serializeCatalogFilters(filters);
    assert.equal(serialized.toString(), 'min=0');
    assert.deepEqual(readCatalogFilters(serialized), filters);
  });

  check('Invalid, blank and unsafe numeric URL inputs use inactive safe defaults', () => {
    for (const query of ['min=nope&max=Infinity', 'min=NaN&max=NaN', 'min=&max=%20', 'min=1e100&max=-1e100']) {
      const filters = read(query);
      assert.equal(filters.min, PRICE_MIN, query);
      assert.equal(filters.max, PRICE_MAX, query);
      assert.equal(hasPriceFilter(filters), false, query);
      assert.equal(applyFilters(GUITARS, filters).length, 200, query);
    }
  });

  check('Negative URL prices normalize to zero and remain explicit', () => {
    const filters = read('min=-15000&max=-1');
    assert.equal(filters.min, 0);
    assert.equal(filters.max, 0);
    assert.equal(hasPriceFilter(filters), true);
    assert.deepEqual(applyFilters(GUITARS, filters), []);
  });

  check('Reversed finite bounds retain the existing min-to-max normalization', () => {
    const filters = read('min=70000&max=30000');
    assert.equal(filters.min, 30000);
    assert.equal(filters.max, 30000);
    assert.deepEqual(applyFilters(GUITARS, filters), []);
  });

  check('An unknown-price-only collection cannot satisfy an explicit budget', () => {
    assert.equal(applyFilters(unknown, defaults).length, unknown.length);
    for (const query of ['min=0', 'max=200000', 'min=70000', 'max=0']) {
      assert.deepEqual(applyFilters(unknown, read(query)), [], query);
    }
  });

  check('Search, brand, category and budget continue to intersect', () => {
    const filters = read('q=Pacifica&brand=Yamaha&type=electric&min=30000&max=40000');
    assert.deepEqual(ids(applyFilters(GUITARS, filters)), [pacifica.id]);
    assert.deepEqual(applyFilters(GUITARS, { ...filters, types: ['bass'] }), []);
    assert.deepEqual(applyFilters(GUITARS, { ...filters, brands: ['Fender'] }), []);
  });

  check('Skipping the price facet preserves unknowns and the other filters', () => {
    const filters = read('brand=Yamaha&min=70000');
    const expected = GUITARS.filter((guitar) => guitar.brand === 'Yamaha');
    assert.deepEqual(ids(applyFilters(GUITARS, filters, 'price')), ids(expected));
    assert.deepEqual(applyFilters(GUITARS, filters), []);
  });

  check('Search, facets, sorting and pagination updates retain high budget URLs', () => {
    const filters = { ...read('min=70000&max=235001'), q: 'Pacifica', brands: ['Yamaha'], types: ['electric'], sort: 'price-asc', page: 3 };
    const serialized = serializeCatalogFilters(filters);
    assert.equal(serialized.get('min'), '70000');
    assert.equal(serialized.get('max'), '235001');
    assert.deepEqual(readCatalogFilters(serialized), filters);
    assert.ok(!serialized.toString().includes('Infinity'));
  });

  check('Reset removes price parameters and preserves the other selected facets', () => {
    const filters = { ...read('q=Pacifica&brand=Yamaha&type=electric&min=70000&sort=price-asc&page=3'), min: PRICE_MIN, max: PRICE_MAX, priceActive: false, page: 1 };
    const serialized = serializeCatalogFilters(filters);
    assert.equal(serialized.has('min'), false);
    assert.equal(serialized.has('max'), false);
    assert.equal(serialized.has('page'), false);
    assert.equal(serialized.get('brand'), 'Yamaha');
    assert.equal(serialized.get('type'), 'electric');
    assert.equal(serialized.get('q'), 'Pacifica');
    assert.equal(serialized.get('sort'), 'price-asc');
    assert.equal(hasPriceFilter(readCatalogFilters(serialized)), false);
  });

  check('Clearing all filters serializes an empty URL and restores all 200 models', () => {
    const serialized = serializeCatalogFilters(defaults);
    assert.equal(serialized.toString(), '');
    assert.equal(applyFilters(GUITARS, readCatalogFilters(serialized)).length, 200);
  });

  check('Malformed sorting, duplicate facets and page bounds retain safe behavior', () => {
    const filters = read('page=NaN&sort=constructor&type=electric,electric,%20bass&brand=Yamaha,Yamaha');
    assert.equal(filters.sort, 'featured');
    assert.equal(filters.page, 1);
    assert.deepEqual(filters.types, ['electric', 'bass']);
    assert.deepEqual(filters.brands, ['Yamaha']);
    assert.equal(read('page=-6').page, 1);
    assert.equal(read('page=2.8').page, 2);
  });

  check('Slider domains remain finite, nonzero and contain high bookmarked bounds', () => {
    for (const [min, max] of [[0, Infinity], [70000, Infinity], [0, 70000], [80000, 235001], [500000, Infinity], [0, 0]]) {
      const domain = getPriceSliderDomain(min, max);
      assert.ok(Number.isFinite(domain));
      assert.ok(domain > 0 && domain > min);
      if (Number.isFinite(max)) assert.ok(domain > max);
      const markup = renderToStaticMarkup(PriceRange({ min, max, onChange() {} }));
      assert.ok(!/NaN|Infinity/.test(markup), `invalid slider markup for ${min}/${max}`);
      assert.equal((markup.match(/type="range"/g) || []).length, 2);
      assert.ok(markup.includes('aria-valuetext='));
    }
  });

  check('The over-70000 preset sends an open maximum and cannot select Pacifica', () => {
    let change;
    const tree = PriceRange({ min: 0, max: PRICE_MAX, onChange: (...args) => { change = args; } });
    const buttons = elements(tree).filter((element) => element.type === 'button');
    assert.equal(buttons.length, 4);
    buttons.at(-1).props.onClick();
    assert.deepEqual(change, [70000, Infinity]);
    const filters = { ...defaults, min: change[0], max: change[1], priceActive: true };
    assert.deepEqual(applyFilters(GUITARS, filters), []);
    assert.equal(serializeCatalogFilters(filters).toString(), 'min=70000');
  });

  check('Moving the maximum slider to its finite endpoint opens the upper bound', () => {
    let change;
    const tree = PriceRange({ min: 70000, max: 90000, onChange: (...args) => { change = args; } });
    const sliders = elements(tree).filter((element) => element.type === 'input' && element.props.type === 'range');
    assert.ok(Number.isFinite(sliders[1].props.max));
    sliders[1].props.onChange({ target: { value: String(sliders[1].props.max) } });
    assert.deepEqual(change, [70000, Infinity]);
    sliders[1].props.onChange({ target: { value: '85000' } });
    assert.deepEqual(change, [70000, 85000]);
  });

  check('A high finite bookmark leaves a native range step to the unbounded endpoint', () => {
    let change;
    const tree = PriceRange({ min: 80000, max: 200000, onChange: (...args) => { change = args; } });
    const maxSlider = elements(tree).filter((element) => element.type === 'input' && element.props.type === 'range')[1];
    assert.equal(maxSlider.props.value, 200000);
    assert.ok(maxSlider.props.value < maxSlider.props.max);
    // Native ArrowRight can now produce a value change; previously a finite
    // bookmarked maximum was already at End and could not become unbounded.
    const next = maxSlider.props.value + maxSlider.props.step;
    assert.equal(next, maxSlider.props.max);
    maxSlider.props.onChange({ target: { value: String(next) } });
    assert.deepEqual(change, [80000, Infinity]);
  });

  check('All 200 IDs, ten brand quotas and archived-model separation are intact', () => {
    assert.equal(GUITARS.length, 200);
    assert.equal(new Set(ids(GUITARS)).size, 200);
    assert.equal(ALL_BRANDS.length, 10);
    for (const brand of ALL_BRANDS) assert.equal(GUITARS.filter((guitar) => guitar.brand === brand).length, 20, brand);
    for (const archive of ARCHIVED_GUITARS) assert.ok(!GUITARS.some((guitar) => guitar.id === archive.id));
  });

  console.log(`\n${passed}/${passed} catalog price checks passed`);
} finally {
  await server.close();
}
