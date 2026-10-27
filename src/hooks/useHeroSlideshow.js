import { useEffect, useRef, useState } from 'react';

const INTERVAL_MS = 6000;
const SWIPE_DISTANCE = 48;
const INTERACTIVE = 'a,button,input,select,textarea,[role="combobox"],[contenteditable="true"]';

/** Decorative photographs: manual swipes never intercept a search or a link. */
export default function useHeroSlideshow(count) {
  const sectionRef = useRef(null);
  const gesture = useRef(null);
  const [active, setActive] = useState(0);
  const [dragging, setDragging] = useState(false);
  const [activity, setActivity] = useState(0);
  const [visible, setVisible] = useState(true);
  const [inView, setInView] = useState(true);
  const [reducedMotion, setReducedMotion] = useState(false);

  useEffect(() => {
    const preference = window.matchMedia('(prefers-reduced-motion: reduce)');
    const updateMotion = () => setReducedMotion(preference.matches);
    const updateVisibility = () => setVisible(!document.hidden);
    updateMotion();
    updateVisibility();
    preference.addEventListener('change', updateMotion);
    document.addEventListener('visibilitychange', updateVisibility);
    const observer = new IntersectionObserver(([entry]) => setInView(entry.isIntersecting), { threshold: 0 });
    if (sectionRef.current) observer.observe(sectionRef.current);
    return () => {
      preference.removeEventListener('change', updateMotion);
      document.removeEventListener('visibilitychange', updateVisibility);
      observer.disconnect();
    };
  }, []);

  useEffect(() => {
    if (count < 2 || reducedMotion || !visible || !inView || dragging) return undefined;
    const timer = window.setInterval(() => setActive((current) => (current + 1) % count), INTERVAL_MS);
    return () => window.clearInterval(timer);
  }, [count, reducedMotion, visible, inView, dragging, activity]);

  const endGesture = (event, cancelled = false) => {
    const start = gesture.current;
    if (!start || start.pointerId !== event.pointerId) return;
    gesture.current = null;
    const dx = event.clientX - start.x;
    const dy = event.clientY - start.y;
    if (!cancelled && Math.abs(dx) >= SWIPE_DISTANCE && Math.abs(dx) > Math.abs(dy) * 1.25) {
      setActive((current) => (current + (dx < 0 ? 1 : count - 1)) % count);
    }
    setDragging(false);
    setActivity((current) => current + 1);
    if (event.currentTarget.hasPointerCapture(event.pointerId)) event.currentTarget.releasePointerCapture(event.pointerId);
  };

  return {
    sectionRef, active, dragging,
    handlers: {
      onPointerDown(event) {
        if (!event.isPrimary || event.button !== 0 || event.target.closest(INTERACTIVE)) return;
        gesture.current = { pointerId: event.pointerId, x: event.clientX, y: event.clientY };
        setDragging(true);
        event.currentTarget.setPointerCapture(event.pointerId);
        // Mouse dragging should move the picture rather than select the title.
        if (event.pointerType === 'mouse') event.preventDefault();
      },
      onPointerUp: (event) => endGesture(event),
      onPointerCancel: (event) => endGesture(event, true),
      onLostPointerCapture(event) {
        if (gesture.current?.pointerId === event.pointerId) {
          gesture.current = null;
          setDragging(false);
          setActivity((current) => current + 1);
        }
      },
    },
  };
}
