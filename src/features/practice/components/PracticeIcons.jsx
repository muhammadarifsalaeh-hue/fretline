const paths = {
  play: <path d="m9 5 11 7-11 7Z" />,
  stop: <rect x="6" y="6" width="12" height="12" rx="2" />,
  reset: <><path d="M3 10a9 9 0 1 1 2.6 8.4M3 4v6h6" /></>,
  eye: <><path d="M2 12s3.5-7 10-7 10 7 10 7-3.5 7-10 7S2 12 2 12Z" /><circle cx="12" cy="12" r="3" /></>,
  minus: <path d="M5 12h14" />,
  plus: <path d="M12 5v14M5 12h14" />,
  left: <path d="m14 6-6 6 6 6" />,
  right: <path d="m10 6 6 6-6 6" />,
  chevron: <path d="m7 10 5 5 5-5" />,
  sound: <><path d="m11 5-6 4H2v6h3l6 4V5Zm4 3a6 6 0 0 1 0 8m3-11a10 10 0 0 1 0 14" /></>,
  search: <><circle cx="10.5" cy="10.5" r="6.5" /><path d="m16 16 4.5 4.5" /></>,
};
export default function PracticeIcon({ name, size = 19 }) {
  return <svg width={size} height={size} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.65" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}
