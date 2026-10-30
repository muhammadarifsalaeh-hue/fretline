import { useEffect, useRef } from 'react';

const SPEED = 30; // CSS pixels per second, independent of refresh rate.
const RESUME_DELAY = 900;
const RESUME_RAMP = 650;
const modulo = (value, width) => ((value % width) + width) % width;

/** Native touch scrolling and a repeated rail share one continuous position. */
export default function useBrandMarquee() {
  const viewportRef = useRef(null);

  useEffect(() => {
    const viewport = viewportRef.current;
    const primary = viewport?.querySelector('[data-marquee-primary]');
    if (!viewport || !primary) return undefined;

    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    let reduced = media.matches;
    let width = 0;
    let position = 0;
    let frame = 0;
    let previousTime = 0;
    let visible = true;
    let focused = false;
    let hovered = false;
    let pointer = null;
    let touching = false;
    let lastInteraction = -Infinity;
    let suppressClickUntil = 0;
    let disposed = false;

    const setMode = (mode) => {
      if (viewport.dataset.marqueeMotion !== mode) viewport.dataset.marqueeMotion = mode;
    };
    const writePosition = (next, normalize = true) => {
      if (!width) return;
      // The middle copy has a full identical copy on either side. Rebasing by
      // precisely one group's measured width never changes the visible logos.
      position = reduced
        ? Math.max(0, Math.min(next, Math.max(0, width - viewport.clientWidth)))
        : normalize ? width + modulo(next - width, width) : next;
      // Adopting a native scroll event must not write its unchanged value back:
      // WebKit treats that assignment as a programmatic scroll and cancels
      // wheel/touch momentum. Only rebasing or an actual requested move writes.
      if (viewport.scrollLeft !== position) viewport.scrollLeft = position;
    };
    const measure = () => {
      const nextWidth = primary.getBoundingClientRect().width;
      if (!nextWidth) return;
      const phase = width ? modulo(position - width, width) / width : 0;
      width = nextWidth;
      writePosition(reduced ? viewport.scrollLeft : width + phase * width);
    };
    const tick = (time) => {
      frame = 0;
      if (disposed || reduced || !visible || document.hidden) return;
      // WebKit can delay the first frames while painting a long photographic
      // page. Discarding elapsed time made the rail run slower on that engine.
      // Use the animation timestamp; hidden/offscreen restarts reset the clock.
      const elapsed = previousTime ? Math.max(0, time - previousTime) : 0;
      previousTime = time;
      const resume = Math.max(0, Math.min(1, (time - lastInteraction - RESUME_DELAY) / RESUME_RAMP));
      const manual = pointer !== null || touching || focused || hovered || resume === 0;
      setMode(focused ? 'keyboard' : hovered ? 'hover' : manual ? 'manual' : 'auto');
      if (!manual) writePosition(position + SPEED * elapsed / 1000 * resume);
      frame = requestAnimationFrame(tick);
    };
    const start = () => {
      if (disposed || frame || reduced || !visible || document.hidden) return;
      previousTime = performance.now();
      frame = requestAnimationFrame(tick);
    };
    const stop = () => { cancelAnimationFrame(frame); frame = 0; previousTime = 0; };

    const onScroll = () => {
      // Browser scroll events also follow our own writes. Ignore rounding
      // differences while retaining fractional phase on high refresh displays.
      if (Math.abs(viewport.scrollLeft - position) <= 1) return;
      lastInteraction = performance.now();
      writePosition(viewport.scrollLeft, !focused);
      setMode(reduced ? 'reduced' : 'manual');
    };
    const onPointerDown = (event) => {
      if (!event.isPrimary || (event.pointerType === 'mouse' && event.button !== 0)) return;
      pointer = { id: event.pointerId, type: event.pointerType, x: event.clientX, y: event.clientY, position: viewport.scrollLeft, dragging: false };
      lastInteraction = performance.now();
      setMode(reduced ? 'reduced' : 'manual');
    };
    const onPointerMove = (event) => {
      if (!pointer || event.pointerId !== pointer.id || pointer.type === 'touch') return;
      const x = event.clientX - pointer.x;
      const y = event.clientY - pointer.y;
      if (!pointer.dragging && Math.abs(x) > 6 && Math.abs(x) > Math.abs(y)) {
        pointer.dragging = true;
        viewport.setPointerCapture(event.pointerId);
        viewport.dataset.marqueeDragging = 'true';
      }
      if (!pointer.dragging) return;
      event.preventDefault();
      lastInteraction = performance.now();
      writePosition(pointer.position - x, !focused);
    };
    const onPointerEnd = (event) => {
      if (event.type === 'blur') touching = false;
      if (!pointer || (event.pointerId !== undefined && event.pointerId !== pointer.id)) return;
      if (pointer.dragging) suppressClickUntil = performance.now() + 500;
      pointer = null;
      delete viewport.dataset.marqueeDragging;
      lastInteraction = performance.now();
    };
    const onClick = (event) => {
      if (event.detail !== 0 && performance.now() < suppressClickUntil) {
        event.preventDefault(); event.stopPropagation();
      }
    };
    const onDragStart = (event) => event.preventDefault();
    const onWheel = () => { lastInteraction = performance.now(); };
    const onPointerEnter = (event) => {
      if (event.pointerType !== 'mouse') return;
      hovered = true;
      setMode(reduced ? 'reduced' : 'hover');
    };
    const onPointerLeave = (event) => {
      if (event.pointerType !== 'mouse') return;
      hovered = false;
      lastInteraction = performance.now();
    };
    // Native panning cancels its PointerEvent early, before the finger lifts.
    // Keep a passive touch lifecycle so a held finger never fights autoplay.
    const onTouchStart = () => { touching = true; lastInteraction = performance.now(); };
    const onTouchEnd = (event) => {
      touching = event.type !== 'touchcancel' && event.touches.length > 0;
      lastInteraction = performance.now();
    };
    const onFocus = (event) => {
      focused = true;
      setMode('keyboard');
      const link = event.target.closest('a');
      if (!link) return;
      const bounds = viewport.getBoundingClientRect();
      const item = link.getBoundingClientRect();
      if (item.left < bounds.left + 8) writePosition(viewport.scrollLeft + item.left - bounds.left - 8, false);
      else if (item.right > bounds.right - 8) writePosition(viewport.scrollLeft + item.right - bounds.right + 8, false);
    };
    const onBlur = (event) => {
      if (viewport.contains(event.relatedTarget)) return;
      focused = false;
      lastInteraction = performance.now();
    };
    const onVisibility = () => { if (document.hidden) stop(); else start(); };
    const onMotion = () => {
      reduced = media.matches;
      pointer = null;
      touching = false;
      focused = false;
      stop();
      measure();
      writePosition(reduced ? 0 : width);
      setMode(reduced ? 'reduced' : 'auto');
      start();
    };
    const observer = new IntersectionObserver(([entry]) => {
      visible = entry.isIntersecting;
      if (visible) start(); else stop();
    }, { rootMargin: '80px 0px', threshold: 0 });
    const resize = new ResizeObserver(measure);
    measure();
    setMode(reduced ? 'reduced' : 'auto');
    observer.observe(viewport);
    resize.observe(viewport);
    resize.observe(primary);
    viewport.addEventListener('scroll', onScroll, { passive: true });
    viewport.addEventListener('pointerdown', onPointerDown);
    viewport.addEventListener('pointerenter', onPointerEnter);
    viewport.addEventListener('pointerleave', onPointerLeave);
    viewport.addEventListener('pointermove', onPointerMove);
    viewport.addEventListener('pointerup', onPointerEnd);
    viewport.addEventListener('pointercancel', onPointerEnd);
    viewport.addEventListener('lostpointercapture', onPointerEnd);
    viewport.addEventListener('click', onClick, true);
    viewport.addEventListener('dragstart', onDragStart);
    viewport.addEventListener('wheel', onWheel, { passive: true });
    viewport.addEventListener('touchstart', onTouchStart, { passive: true });
    viewport.addEventListener('touchend', onTouchEnd, { passive: true });
    viewport.addEventListener('touchcancel', onTouchEnd, { passive: true });
    viewport.addEventListener('focusin', onFocus);
    viewport.addEventListener('focusout', onBlur);
    window.addEventListener('pointerup', onPointerEnd);
    window.addEventListener('pointercancel', onPointerEnd);
    window.addEventListener('blur', onPointerEnd);
    document.addEventListener('visibilitychange', onVisibility);
    media.addEventListener('change', onMotion);
    start();

    return () => {
      disposed = true;
      stop();
      observer.disconnect(); resize.disconnect();
      viewport.removeEventListener('scroll', onScroll);
      viewport.removeEventListener('pointerdown', onPointerDown);
      viewport.removeEventListener('pointerenter', onPointerEnter);
      viewport.removeEventListener('pointerleave', onPointerLeave);
      viewport.removeEventListener('pointermove', onPointerMove);
      viewport.removeEventListener('pointerup', onPointerEnd);
      viewport.removeEventListener('pointercancel', onPointerEnd);
      viewport.removeEventListener('lostpointercapture', onPointerEnd);
      viewport.removeEventListener('click', onClick, true);
      viewport.removeEventListener('dragstart', onDragStart);
      viewport.removeEventListener('wheel', onWheel);
      viewport.removeEventListener('touchstart', onTouchStart);
      viewport.removeEventListener('touchend', onTouchEnd);
      viewport.removeEventListener('touchcancel', onTouchEnd);
      viewport.removeEventListener('focusin', onFocus);
      viewport.removeEventListener('focusout', onBlur);
      window.removeEventListener('pointerup', onPointerEnd);
      window.removeEventListener('pointercancel', onPointerEnd);
      window.removeEventListener('blur', onPointerEnd);
      document.removeEventListener('visibilitychange', onVisibility);
      media.removeEventListener('change', onMotion);
    };
  }, []);

  return viewportRef;
}
