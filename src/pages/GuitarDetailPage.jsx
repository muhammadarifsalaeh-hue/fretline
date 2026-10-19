import { t } from '@/i18n';
import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import ColorSwatches from '@/components/detail/ColorSwatches';
import DataStatusNote from '@/components/detail/DataStatusNote';
import GuitarGallery from '@/components/detail/GuitarGallery';
import SimilarGuitars from '@/components/detail/SimilarGuitars';
import SpecTable from '@/components/detail/SpecTable';
import StickyGuitarBar from '@/components/detail/StickyGuitarBar';
import AppLink from '@/components/ui/AppLink';
import Badge from '@/components/ui/Badge';
import { CheckIcon, HeartIcon, PlusIcon } from '@/components/ui/Icons';
import Reveal from '@/components/ui/Reveal';
import { CATEGORIES } from '@/data/categories';
import { GUITARS_BY_ID } from '@/data/guitars';
import { useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { NOT_SPECIFIED, formatKg, formatPrice } from '@/utils/format';
import { brandUrl, categoryUrl } from '@/utils/routes';
import NotFoundPage from './NotFoundPage';

// ประโยคแรกของ description ใช้เป็นสรุปสั้นใต้ชื่อรุ่น
const firstSentence = (text) => (text.includes('. ') ? `${text.split('. ')[0]}.` : text);

function DetailContent({ guitar }) {
  const { compare, wishlist, toggleCompare, toggleWishlist } = useShop();
  const [colorIndex, setColorIndex] = useState(0);
  const [stuck, setStuck] = useState(false);
  const ctaRef = useRef(null);

  const inCompare = compare.includes(guitar.id);
  const inWishlist = wishlist.includes(guitar.id);
  const categoryName = CATEGORIES.find((c) => c.id === guitar.category)?.name;

  useEffect(() => {
    document.title = `${guitar.brand} ${guitar.name} — Fretline`;
  }, [guitar]);

  // แสดงแถบสรุปเมื่อปุ่ม Add to compare เลื่อนพ้นขอบบนของจอ
  useEffect(() => {
    const el = ctaRef.current;
    if (!el || !('IntersectionObserver' in window)) return undefined;
    const io = new IntersectionObserver(([entry]) => setStuck(!entry.isIntersecting && entry.boundingClientRect.top < 0));
    io.observe(el);
    return () => io.disconnect();
  }, []);

  const saving = guitar.oldPrice && guitar.price != null ? guitar.oldPrice - guitar.price : 0;
  const keyFeatures = [
    { label: t('detail.tone'), value: guitar.specs.pickups ?? NOT_SPECIFIED },
    {
      label: t('detail.feel'),
      value:
        [guitar.specs.scale != null && t('detail.scaleTxt', { n: guitar.specs.scale }), guitar.specs.frets != null && t('detail.fretsTxt', { n: guitar.specs.frets })].filter(Boolean).join(', ') ||
        NOT_SPECIFIED,
    },
    { label: t('detail.build'), value: guitar.specs.body ?? NOT_SPECIFIED },
  ];

  return (
    <>
      <StickyGuitarBar guitar={guitar} visible={stuck} inCompare={inCompare} onToggleCompare={() => toggleCompare(guitar)} />

      {/* ส่วนบน: Gallery + ข้อมูลหลัก */}
      <section className="container-x pb-20 pt-28 md:pt-36 lg:pb-28">
        <nav aria-label={t('common.breadcrumb')} className="mb-8 flex flex-wrap items-center gap-2 text-sm text-mute">
          <AppLink href="/" className="transition-colors hover:text-bone">{t('nav.home')}</AppLink>
          <span aria-hidden="true">/</span>
          <AppLink href="/guitars" className="transition-colors hover:text-bone">{t('nav.guitars')}</AppLink>
          <span aria-hidden="true">/</span>
          <AppLink href={categoryUrl(guitar.category)} className="transition-colors hover:text-bone">{categoryName}</AppLink>
          <span aria-hidden="true">/</span>
          <span className="text-bone/80">{guitar.name}</span>
        </nav>

        <div className="grid gap-10 lg:grid-cols-12 lg:gap-16">
          <div className="lg:col-span-7 lg:self-start xl:sticky xl:top-28">
            <GuitarGallery guitar={guitar} />
          </div>

          <div className="lg:col-span-5 lg:pt-2">
            <AppLink
              href={brandUrl(guitar.brand)}
              className="text-xs uppercase tracking-[0.18em] text-mute transition-colors hover:text-gold"
            >
              {guitar.brand}
            </AppLink>
            <h1 className="mt-3 font-serif text-5xl leading-[1.02] tracking-tight md:text-6xl">{guitar.name}</h1>
            <p className="mt-4">
              <span className="inline-flex rounded-full border border-gold/40 px-3 py-1 text-xs text-gold">{t(`status.${guitar.dataStatus ?? 'sample'}`)}</span>
            </p>
            {guitar.rating && (
              <p className="mt-4 flex items-center gap-2 text-sm">
                <span className="font-mono text-gold">★ {guitar.rating.score.toFixed(1)}</span>
                <span className="text-mute">{guitar.rating.count} reviews</span>
              </p>
            )}
            <p className="mt-5 max-w-md text-base leading-relaxed text-bone/70">{firstSentence(guitar.description)}</p>

            <div className="mt-8 flex flex-wrap items-baseline gap-x-4 gap-y-2">
              <span className="font-mono text-4xl text-gold">{formatPrice(guitar.price)}</span>
              {guitar.oldPrice && <span className="font-mono text-lg text-mute line-through">{formatPrice(guitar.oldPrice)}</span>}
              {saving > 0 && <Badge type="SALE" />}
            </div>
            <p className="mt-2 text-xs text-mute">
              {guitar.price == null
                ? t('detail.noPrice')
                : `${saving > 0 ? t('detail.saving', { amount: formatPrice(saving) }) : ''}${t('detail.priceNote')}`}
            </p>

            <dl className="mt-8 grid grid-cols-3 gap-px overflow-hidden rounded-2xl border border-line bg-line">
              {[
                [t('filter.type'), categoryName],
                [t('row.strings'), guitar.specs.strings ?? NOT_SPECIFIED],
                [t('row.weight'), formatKg(guitar.specs.weightKg)],
              ].map(([label, value]) => (
                <div key={label} className="bg-ink px-4 py-4">
                  <dt className="text-xs text-mute">{label}</dt>
                  <dd className="mt-1 font-mono text-sm text-bone">{value}</dd>
                </div>
              ))}
            </dl>

            <div className="mt-8">
              <ColorSwatches colors={guitar.colors} value={colorIndex} onChange={setColorIndex} />
            </div>

            <div ref={ctaRef} className="mt-10 flex flex-col gap-3 sm:flex-row">
              <button
                type="button"
                onClick={() => toggleCompare(guitar)}
                aria-pressed={inCompare}
                className={cn(
                  'inline-flex h-14 flex-1 items-center justify-center gap-2 rounded-full px-8 text-[15px] font-medium transition duration-300 ease-premium active:scale-[0.98]',
                  inCompare ? 'border border-gold bg-gold/10 text-gold' : 'bg-gold text-ink hover:bg-gold-soft',
                )}
              >
                {inCompare ? <CheckIcon size={18} /> : <PlusIcon size={18} />}
                {inCompare ? t('detail.added') : t('detail.add')}
              </button>
              <button
                type="button"
                onClick={() => toggleWishlist(guitar)}
                aria-pressed={inWishlist}
                className={cn(
                  'inline-flex h-14 items-center justify-center gap-2 rounded-full border px-7 text-[15px] transition duration-300 ease-premium active:scale-[0.98]',
                  inWishlist ? 'border-gold bg-gold/10 text-gold' : 'border-white/20 hover:border-gold hover:text-gold',
                )}
              >
                <HeartIcon size={18} fill={inWishlist ? 'currentColor' : 'none'} />
                {inWishlist ? t('detail.saved') : t('detail.saveBtn')}
              </button>
            </div>
            {inCompare && (
              <AppLink href="/compare" className="mt-4 inline-block text-sm text-gold transition-colors hover:text-gold-soft">
                {t('detail.viewComparison', { n: compare.length })}
              </AppLink>
            )}
          </div>
        </div>
      </section>

      {/* About */}
      <section className="border-t border-line py-16 md:py-24">
        <div className="container-x grid gap-10 lg:grid-cols-12 lg:gap-16">
          <Reveal className="lg:col-span-6">
            <h2 className="font-sans text-3xl font-medium leading-[1.1] tracking-tight md:text-4xl">{t('detail.about')}</h2>
            <p className="mt-6 max-w-xl text-lg leading-relaxed text-bone/75">{guitar.description}</p>
          </Reveal>
          <Reveal delay={120} className="lg:col-span-6">
            <ul className="grid gap-4 sm:grid-cols-3 lg:grid-cols-1 xl:grid-cols-3">
              {keyFeatures.map((f) => (
                <li key={f.label} className="rounded-2xl border border-line bg-surface p-6">
                  <p className="text-xs text-mute">{f.label}</p>
                  <p className="mt-3 font-mono text-[13px] leading-relaxed text-bone">{f.value}</p>
                </li>
              ))}
            </ul>
          </Reveal>
        </div>
      </section>

      {/* Specifications */}
      <section id="specs" className="bg-surface py-16 md:py-24">
        <div className="container-x">
          <Reveal>
            <h2 className="mb-10 font-sans text-3xl font-medium leading-[1.1] tracking-tight md:mb-14 md:text-4xl">{t('detail.specs')}</h2>
          </Reveal>
          <DataStatusNote guitar={guitar} />
          <SpecTable guitar={guitar} />
        </div>
      </section>

      <SimilarGuitars guitar={guitar} />
    </>
  );
}

export default function GuitarDetailPage() {
  const { slug } = useParams();
  const guitar = GUITARS_BY_ID[slug];
  if (!guitar) return <NotFoundPage />;
  // key = id → เปลี่ยนรุ่นแล้ว state (สี, gallery) รีเซ็ตเอง
  return <DetailContent key={guitar.id} guitar={guitar} />;
}
