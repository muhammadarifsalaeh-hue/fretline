import assert from 'node:assert/strict';
import { createServer } from 'vite';

const server = await createServer({ server: { middlewareMode: true, hmr: false }, appType: 'custom', logLevel: 'error' });
let passed = 0;
const check = (name, fn) => { fn(); passed++; console.log(`PASS ${name}`); };
try {
  const { trustedPrice, publicPrice, hasListedRetailerPrice, hasManufacturerRrp } = await server.ssrLoadModule('/src/utils/dataTrust.js');
  const { formatPrice } = await server.ssrLoadModule('/src/utils/format.js');
  const source = { url: 'https://manufacturer.example/product', verifiedOn: '2026-10-29', fields: ['price'] };
  const shop = { url: 'https://retailer.example/product', verifiedOn: '2026-10-29', currency: 'THB', kind: 'retailer-listed', retailer: 'QA retailer' };
  const guitar = { price: 30600, dataStatus: 'partial', source, priceSource: shop };
  check('a verified THB retailer listing is displayed without requiring the old Yamaha import batch', () => {
    assert.equal(publicPrice(guitar), '฿30,600');
    assert.equal(hasListedRetailerPrice(guitar), true);
    assert.equal(hasManufacturerRrp(guitar), false);
  });
  check('missing, zero, negative, non-finite and string product prices become a quote request', () => {
    for (const price of [null, undefined, 0, -1, NaN, Infinity, '30600']) {
      const value = { ...guitar, price };
      assert.equal(trustedPrice(value), null);
      assert.equal(publicPrice(value), 'สอบถามราคา');
      assert.equal(hasListedRetailerPrice(value), false);
    }
  });
  check('unverified, foreign-currency and unsourced prices are not exposed', () => {
    for (const value of [
      { ...guitar, dataStatus: 'sample' },
      { ...guitar, source: null },
      { ...guitar, source: { ...source, fields: [] } },
      { ...guitar, priceSource: { ...shop, currency: 'USD' } },
      { ...guitar, priceSource: { ...shop, verifiedOn: '' } },
    ]) assert.equal(publicPrice(value), 'สอบถามราคา');
  });
  check('manufacturer RRP and retailer sale prices remain distinct', () => {
    const rrp = { ...guitar, price: 34000, priceSource: { ...shop, kind: 'manufacturer-recommended-retail' } };
    assert.equal(hasManufacturerRrp(rrp), true);
    assert.equal(hasListedRetailerPrice(rrp), false);
    assert.equal(publicPrice(rrp), '฿34,000');
  });
  check('a legitimate zero budget boundary is retained while null product prices request a quote', () => {
    assert.equal(formatPrice(0), '฿0');
    assert.equal(formatPrice(null), 'สอบถามราคา');
    assert.equal(publicPrice({ ...guitar, price: 0 }), 'สอบถามราคา');
  });
  console.log(`\n${passed}/${passed} public price checks passed`);
} finally { await server.close(); }
