import { useEffect, useMemo, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { escapeRegExp, searchCatalog } from '@/utils/search';
import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import AppLink from '@/components/ui/AppLink';
import { SearchIcon } from '@/components/ui/Icons';
import GuitarImage from '@/components/guitar/GuitarImage';

// ชิปทางลัด: พาไป Catalog พร้อมตัวกรองจริง (ไม่ใช่แค่เติมคำค้น)
const QUICK_CHIPS = [
  { label: t('chip.budget'), href: '/guitars?max=20000' },
  { label: t('chip.beginner'), href: `/guitars?q=${encodeURIComponent(t('chip.beginner'))}` },
  { label: t('chip.left'), href: `/guitars?q=${encodeURIComponent(t('chip.left'))}` },
  { label: t('category.acoustic'), href: '/guitars?type=acoustic' },
  { label: t('category.electric'), href: '/guitars?type=electric' },
];

/** ไฮไลต์ตัวอักษรที่ตรงกับคำค้น */
function Highlight({ text, query }) {
  const q = query.trim();
  if (!q) return text;
  const parts = text.split(new RegExp(`(${escapeRegExp(q)})`, 'ig'));
  return parts.map((part, i) =>
    part.toLowerCase() === q.toLowerCase() ? (
      <mark key={i} className="bg-transparent text-gold">{part}</mark>
    ) : (
      part
    ),
  );
}

/** ช่องค้นหาใน Hero: autocomplete แบ่งกลุ่ม + ใช้คีย์บอร์ดได้ (↑ ↓ Enter Esc) */
export default function SearchBar({ showSuggestions = true }) {
  const [query, setQuery] = useState('');
  const [open, setOpen] = useState(false);
  const [active, setActive] = useState(-1);
  const wrapRef = useRef(null);
  const navigate = useNavigate();

  const groups = useMemo(() => searchCatalog(query), [query]);
  const flat = useMemo(() => groups.flatMap((g) => g.items), [groups]);
  const showList = open && query.trim().length > 0;

  // ปิด dropdown เมื่อคลิกนอกกล่อง
  useEffect(() => {
    const onDown = (e) => {
      if (wrapRef.current && !wrapRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener('pointerdown', onDown);
    return () => document.removeEventListener('pointerdown', onDown);
  }, []);

  const go = (href) => {
    setOpen(false);
    navigate(href);
  };

  // กด Enter / ปุ่ม Search → ไปหน้า Catalog พร้อมคำค้น
  const submit = () => {
    const q = query.trim();
    go(q ? `/guitars?q=${encodeURIComponent(q)}` : '/guitars');
  };

  const select = (item) => {
    setQuery(item.label);
    go(item.href);
  };

  const onKeyDown = (e) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setOpen(true);
      setActive((i) => (flat.length ? (i + 1) % flat.length : -1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActive((i) => (flat.length ? (i <= 0 ? flat.length - 1 : i - 1) : -1));
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (showList && active >= 0 && flat[active]) select(flat[active]);
      else submit();
    } else if (e.key === 'Escape') {
      setOpen(false);
      setActive(-1);
    }
  };

  let index = -1;

  return (
    <div ref={wrapRef} id="search" onBlur={(event) => { if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false); }} className="relative w-full max-w-[560px]">
      <div className="flex h-14 items-center gap-3 rounded-xl border border-white/15 bg-white/[0.06] pl-5 pr-2 backdrop-blur-md transition duration-300 focus-within:border-gold focus-within:shadow-[0_0_0_4px_rgba(200,161,90,0.14)]">
        <SearchIcon className="shrink-0 text-mute" />
        <input
          id="hero-search"
          type="text"
          role="combobox"
          aria-expanded={showList}
          aria-controls={showList ? 'search-results' : undefined}
          aria-autocomplete="list"
          aria-activedescendant={showList && active >= 0 && flat[active] ? `search-option-${active}` : undefined}
          aria-label={t('search.aria')}
          autoComplete="off"
          value={query}
          placeholder={t('search.placeholder')}
          onChange={(e) => {
            setQuery(e.target.value);
            setOpen(true);
            setActive(-1);
          }}
          onFocus={() => setOpen(true)}
          onKeyDown={onKeyDown}
          className="h-full min-w-0 flex-1 bg-transparent text-[15px] text-bone placeholder:text-mute focus:outline-none"
        />
        <button
          type="button"
          onClick={submit}
          className="h-11 shrink-0 rounded-lg bg-gold px-4 text-sm font-medium text-ink transition hover:bg-gold-soft"
        >
          {t('search.button')}
        </button>
      </div>

      {/* ทางลัด */}
      {showSuggestions && <ul className="mt-4 flex flex-wrap gap-2">
        {QUICK_CHIPS.map((chip) => (
          <li key={chip.label}>
            <AppLink
              href={chip.href}
              className="inline-flex min-h-[44px] items-center rounded-full border border-white/[0.12] px-4 text-[13px] text-bone/75 transition duration-300 hover:border-gold hover:text-gold"
            >
              {chip.label}
            </AppLink>
          </li>
        ))}
      </ul>}

      {/* Autocomplete */}
      {showList && (
        <div
          id="search-results"
          role="listbox"
          aria-label={t('search.aria')}
          className="absolute left-0 right-0 top-[60px] z-30 max-h-[50vh] overflow-y-auto rounded-3xl border border-line bg-surface/95 p-2 shadow-[0_30px_80px_-20px_rgba(0,0,0,0.9)] backdrop-blur-xl"
        >
          {groups.length === 0 ? (
            <p className="px-4 py-6 text-sm text-mute">
              {t('search.noMatch', { q: query.trim() })}
            </p>
          ) : (
            groups.map((group) => (
              <div key={group.title} className="py-1">
                <p className="px-4 pb-1 pt-2 text-xs text-mute">{group.title}</p>
                {group.items.map((item) => {
                  index += 1;
                  const isActive = index === active;
                  return (
                    <button
                      key={item.key}
                      id={`search-option-${index}`}
                      type="button"
                      tabIndex={-1}
                      role="option"
                      aria-selected={isActive}
                      onMouseDown={(e) => e.preventDefault()}
                      onClick={() => select(item)}
                      className={cn(
                        'flex w-full items-center gap-3 rounded-2xl px-3 py-2.5 text-left transition-colors',
                        isActive ? 'bg-white/10' : 'hover:bg-white/5',
                      )}
                    >
                      {item.guitar && <GuitarImage guitar={item.guitar} size="sm" alt="" className="h-11 w-11 shrink-0 rounded-lg" />}
                      <span className="min-w-0 flex-1 truncate text-sm">
                        <Highlight text={item.label} query={query} />
                      </span>
                      <span className="shrink-0 font-mono text-xs text-mute">{item.meta}</span>
                    </button>
                  );
                })}
              </div>
            ))
          )}
        </div>
      )}
    </div>
  );
}
