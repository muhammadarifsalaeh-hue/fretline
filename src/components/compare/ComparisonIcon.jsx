/** Shared, lightweight symbols for this comparison experience. */
export default function ComparisonIcon({ name = 'specs', size = 22, ...props }) {
  const paths = {
    specs: <><path d="M5 3v18M12 3v18M19 3v18" /><path d="M2 8h6m1 8h6m1-10h6" /><circle cx="5" cy="8" r="2" /><circle cx="12" cy="16" r="2" /><circle cx="19" cy="6" r="2" /></>,
    tone: <><path d="M2 12h3l2-7 4 15 3-17 3 13 2-4h3" /></>,
    star: <path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9Z" />,
    share: <><circle cx="6" cy="12" r="2.5" /><circle cx="18" cy="5" r="2.5" /><circle cx="18" cy="19" r="2.5" /><path d="m8.2 10.7 7.6-4.4M8.2 13.3l7.6 4.4" /></>,
    materials: <><path d="m12 3 9 5-9 5-9-5 9-5Zm-9 9 9 5 9-5M3 16l9 5 9-5" /></>,
    hardware: <><path d="m14 3 2 3 4 1 1 4-3 3-1 4-4 1-3-3-4-1-1-4 3-3 1-4Z" /><circle cx="12" cy="11" r="3" /></>,
    dimensions: <><rect x="3" y="6" width="18" height="12" rx="2" /><path d="M7 6v4m5-4v6m5-6v4" /></>,
    all: <><rect x="3" y="3" width="7" height="7" rx="1" /><rect x="14" y="3" width="7" height="7" rx="1" /><rect x="3" y="14" width="7" height="7" rx="1" /><rect x="14" y="14" width="7" height="7" rx="1" /></>,
    trash: <><path d="M4 7h16M9 7V4h6v3M6 7l1 14h10l1-14M10 11v6m4-6v6" /></>,
  };
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] ?? paths.specs}</svg>;
}
