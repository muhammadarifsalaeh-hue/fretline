/**
 * Run: node docs/signature-redesign/phase-b/tests/scroll-focus.mjs
 * Exercises the real DOM helpers with a mocked browser boundary. Native touch
 * keyboard activation, layout and route lifecycle still need browser testing.
 */
import assert from 'node:assert/strict';
import test from 'node:test';
import {
  focusSearch,
  preferredScrollBehavior,
  scrollToElement,
  scrollToPosition,
  scrollToTop,
} from '../../../../src/utils/dom.js';

function browserFixture(t, { reduced = false, fields = {} } = {}) {
  const previousWindow = Object.getOwnPropertyDescriptor(globalThis, 'window');
  const previousDocument = Object.getOwnPropertyDescriptor(globalThis, 'document');
  const calls = [];
  const input = (name) => ({
    focus: (options) => calls.push({ action: 'focus', name, options }),
    scrollIntoView: (options) => calls.push({ action: 'element-scroll', name, options }),
  });

  globalThis.window = {
    matchMedia: () => ({ matches: reduced }),
    scrollTo: (options) => calls.push({ action: 'window-scroll', options }),
  };
  globalThis.document = { getElementById: (id) => fields[id] ?? null };
  t.after(() => {
    if (previousWindow) Object.defineProperty(globalThis, 'window', previousWindow);
    else delete globalThis.window;
    if (previousDocument) Object.defineProperty(globalThis, 'document', previousDocument);
    else delete globalThis.document;
  });
  return { calls, fields, input };
}

test('scroll-to-top defaults to both origins and permits caller options', (t) => {
  const { calls } = browserFixture(t);
  scrollToTop();
  scrollToTop({ left: 24, behavior: 'auto' });
  assert.deepEqual(calls, [
    { action: 'window-scroll', options: { top: 0, left: 0, behavior: 'smooth' } },
    { action: 'window-scroll', options: { top: 0, left: 24, behavior: 'auto' } },
  ]);
});

test('reduced motion removes smooth movement without changing coordinates', (t) => {
  const { calls } = browserFixture(t, { reduced: true });
  assert.equal(preferredScrollBehavior(), 'auto');
  assert.equal(preferredScrollBehavior('auto'), 'auto');
  scrollToPosition({ top: 150, left: 20, behavior: 'smooth' });
  assert.deepEqual(calls, [
    { action: 'window-scroll', options: { top: 150, left: 20, behavior: 'auto' } },
  ]);
});

test('element scrolling preserves placement and handles an absent target', (t) => {
  const { calls, input } = browserFixture(t, { reduced: true });
  assert.equal(scrollToElement(null), false);
  assert.equal(scrollToElement(input('target'), { block: 'end', inline: 'center' }), true);
  assert.deepEqual(calls, [
    { action: 'element-scroll', name: 'target', options: { block: 'end', inline: 'center', behavior: 'auto' } },
  ]);
});

test('search focuses synchronously before scrolling and uses the current page field', (t) => {
  const { calls, fields, input } = browserFixture(t, { reduced: true });
  fields['catalog-search'] = input('catalog');
  fields['brands-search'] = input('brands');
  fields['hero-search'] = input('hero');

  assert.equal(focusSearch(), true);
  assert.deepEqual(calls, [
    { action: 'focus', name: 'catalog', options: { preventScroll: true } },
    { action: 'element-scroll', name: 'catalog', options: { block: 'center', inline: 'nearest', behavior: 'auto' } },
  ]);

  delete fields['catalog-search'];
  calls.length = 0;
  assert.equal(focusSearch(), true);
  assert.equal(calls[0].name, 'brands');

  delete fields['brands-search'];
  calls.length = 0;
  assert.equal(focusSearch(), true);
  assert.equal(calls[0].name, 'hero');
});

test('search reports an absent field without moving focus or scrolling', (t) => {
  const { calls } = browserFixture(t);
  assert.equal(focusSearch(), false);
  assert.deepEqual(calls, []);
});

test('helpers tolerate a browser without matchMedia and server-side scrolling', (t) => {
  const { calls } = browserFixture(t);
  delete window.matchMedia;
  assert.equal(preferredScrollBehavior(), 'smooth');
  scrollToTop();
  assert.equal(calls[0].options.behavior, 'smooth');

  delete globalThis.window;
  assert.equal(preferredScrollBehavior(), 'smooth');
  assert.doesNotThrow(() => scrollToTop());
});
