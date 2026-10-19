// ไอคอนแบบ inline SVG (ไม่ต้องติดตั้งไลบรารีเพิ่ม)
const make = (paths) =>
  function Icon({ size = 20, className = '', ...props }) {
    return (
      <svg
        width={size}
        height={size}
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
        aria-hidden="true"
        className={className}
        {...props}
      >
        {paths}
      </svg>
    );
  };

export const SearchIcon = make(
  <>
    <circle cx="11" cy="11" r="7" />
    <path d="m20 20-3.5-3.5" />
  </>,
);
export const HeartIcon = make(
  <path d="M20.8 4.6a5.5 5.5 0 0 0-7.8 0L12 5.7l-1-1.1a5.5 5.5 0 0 0-7.8 7.8l1 1.1L12 21.3l7.8-7.8 1-1.1a5.5 5.5 0 0 0 0-7.8z" />,
);
export const PlusIcon = make(<path d="M12 5v14M5 12h14" />);
export const CheckIcon = make(<path d="m5 12.5 4.5 4.5L19 7.5" />);
export const ArrowRightIcon = make(<path d="M5 12h14m-6-6 6 6-6 6" />);
export const ArrowUpRightIcon = make(<path d="M7 17 17 7M8 7h9v9" />);
export const CloseIcon = make(<path d="M6 6l12 12M18 6 6 18" />);
export const MenuIcon = make(<path d="M4 8h16M4 16h16" />);
export const ChevronLeftIcon = make(<path d="m15 6-6 6 6 6" />);
export const ChevronRightIcon = make(<path d="m9 6 6 6-6 6" />);
export const ChevronDownIcon = make(<path d="m6 9 6 6 6-6" />);
export const UserIcon = make(
  <>
    <circle cx="12" cy="8" r="4" />
    <path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6" />
  </>,
);
export const HomeIcon = make(<path d="M4 11 12 4l8 7v9H4zM10 20v-6h4v6" />);
export const CompareIcon = make(
  <>
    <rect x="3" y="4" width="7" height="16" rx="1.5" />
    <rect x="14" y="4" width="7" height="16" rx="1.5" />
  </>,
);
export const ExpandIcon = make(<path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5" />);
export const TruckIcon = make(
  <>
    <path d="M3 6h11v10H3zM14 9h4l3 3v4h-7" />
    <circle cx="7.5" cy="17.5" r="1.8" />
    <circle cx="17.5" cy="17.5" r="1.8" />
  </>,
);
export const ShieldIcon = make(<path d="M12 3 4.5 6v5.5c0 4.4 3 8 7.5 9.5 4.5-1.5 7.5-5.1 7.5-9.5V6z" />);
export const ReturnIcon = make(<path d="M9 14 4 9l5-5M4 9h10a6 6 0 0 1 0 12h-3" />);
export const GuitarIcon = make(
  <>
    <circle cx="9" cy="15" r="5" />
    <circle cx="9" cy="15" r="1.2" />
    <path d="m12.5 11.5 7-7" />
    <path d="m17 3 4 4" />
  </>,
);
export const TagIcon = make(
  <>
    <path d="M3 12V4h8l9.5 9.5a2 2 0 0 1 0 2.8l-4.2 4.2a2 2 0 0 1-2.8 0z" />
    <circle cx="7.5" cy="8.5" r="1.2" />
  </>,
);
export const GridIcon = make(
  <>
    <rect x="4" y="4" width="7" height="7" rx="1.2" />
    <rect x="13" y="4" width="7" height="7" rx="1.2" />
    <rect x="4" y="13" width="7" height="7" rx="1.2" />
    <rect x="13" y="13" width="7" height="7" rx="1.2" />
  </>,
);
