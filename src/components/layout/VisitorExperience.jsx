import { useEffect, useRef } from 'react';
import { useLocation } from 'react-router-dom';
import '@/styles/experience-system.css';
import '@/styles/experience-home.css';
import '@/styles/experience-showroom.css';
import '@/styles/experience-tools.css';

// This boundary owns presentation only. Admin retains the original tokens and
// styling; providers, authentication, route elements and stored data stay put.
export default function VisitorExperience({ children }) {
  const { pathname } = useLocation();
  const root = useRef(null);
  const enabled = pathname.replace(/\/$/, '') !== '/admin';

  useEffect(() => {
    if (!enabled || !root.current || !('IntersectionObserver' in window)) return undefined;
    const media = window.matchMedia('(prefers-reduced-motion: reduce)');
    const element = root.current;
    const targets = new Set();
    const selector = '.signature-category-grid, .home-editorial-copy, .signature-collection-controls, .brand-directory-card, .detail-key-features, .wishlist-empty';
    const observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        entry.target.dataset.experienceVisible = 'true';
        observer.unobserve(entry.target);
      });
    }, { threshold: 0.05, rootMargin: '0px 0px 48px 0px' });
    const scan = () => {
      element.querySelectorAll(selector).forEach((target) => {
        if (targets.has(target)) return;
        targets.add(target);
        // Progressive enhancement: never hide content already on screen.
        if (media.matches || target.getBoundingClientRect().top < innerHeight) return;
        target.dataset.experienceReveal = 'true';
        observer.observe(target);
      });
    };
    const showAll = () => {
      if (media.matches) targets.forEach((target) => { target.dataset.experienceVisible = 'true'; observer.unobserve(target); });
    };
    scan();
    const mutations = new MutationObserver(scan);
    mutations.observe(element.querySelector('main') ?? element, { childList: true, subtree: true });
    media.addEventListener('change', showAll);
    return () => {
      observer.disconnect(); mutations.disconnect(); media.removeEventListener('change', showAll);
      targets.forEach((target) => { delete target.dataset.experienceReveal; delete target.dataset.experienceVisible; });
    };
  }, [enabled, pathname]);

  return <div ref={root} className={enabled ? 'fretline-experience' : undefined} data-visitor-experience={enabled ? true : undefined}>{children}</div>;
}
