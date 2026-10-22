/** Keep programmatic scrolling consistent with the visitor's motion setting. */
export function preferredScrollBehavior(behavior = 'smooth') {
  const reduceMotion = typeof window !== 'undefined'
    && window.matchMedia?.('(prefers-reduced-motion: reduce)').matches;
  return reduceMotion && behavior === 'smooth' ? 'auto' : behavior;
}

export function scrollToPosition(options = {}) {
  if (typeof window === 'undefined') return;
  window.scrollTo({ ...options, behavior: preferredScrollBehavior(options.behavior) });
}

export function scrollToTop(options = {}) {
  scrollToPosition({ top: 0, left: 0, ...options });
}

export function scrollToElement(element, options = {}) {
  if (!element) return false;
  element.scrollIntoView({
    block: 'start',
    inline: 'nearest',
    ...options,
    behavior: preferredScrollBehavior(options.behavior),
  });
  return true;
}

/** Focus during the touch/click gesture so iPad Safari can open its keyboard. */
export function focusSearch() {
  const input = document.getElementById('catalog-search')
    || document.getElementById('brands-search')
    || document.getElementById('hero-search');
  if (!input) return false;
  input.focus({ preventScroll: true });
  scrollToElement(input, { block: 'center' });
  return true;
}
