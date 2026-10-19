import { useEffect } from 'react';
import { useParams } from 'react-router-dom';
import CatalogCard from '@/components/catalog/CatalogCard';
import AppLink from '@/components/ui/AppLink';
import Button from '@/components/ui/Button';
import { BRANDS, BRANDS_BY_ID, getBrandGuitars } from '@/data/brands';
import { CATEGORIES } from '@/data/categories';
import { formatPrice } from '@/utils/format';
import { brandCatalogUrl, brandUrl } from '@/utils/routes';
import NotFoundPage from './NotFoundPage';

const typeName = (id) => CATEGORIES.find((c) => c.id === id)?.name ?? id;

/** /brands/:id — กีตาร์ทั้งหมดของแบรนด์นั้น (ใช้ CatalogCard ตัวเดียวกับ Catalog) */
function BrandContent({ brand }) {
  const guitars = getBrandGuitars(brand.name);
  const others = BRANDS.filter((b) => b.id !== brand.id);
  const meta = [brand.country, brand.founded && `Est. ${brand.founded}`].filter(Boolean).join(', ');

  useEffect(() => {
    document.title = `${brand.name} guitars — Fretline`;
  }, [brand]);

  const stats = [
    ['Models', brand.models],
    ['Price range', brand.priceMin == null ? formatPrice(null) : brand.priceMin === brand.priceMax ? formatPrice(brand.priceMin) : `${formatPrice(brand.priceMin)} – ${formatPrice(brand.priceMax)} (listed prices)`],
    ['Types', brand.categories.map(typeName).join(', ')],
  ];

  return (
    <>
      <header className="relative isolate border-b border-line pb-12 pt-28 md:pb-16 md:pt-36">
        <div aria-hidden="true" className="pointer-events-none absolute inset-0 -z-10 bg-[radial-gradient(50%_80%_at_80%_0%,#262626_0%,#0A0A0A_70%)]" />
        <div className="container-x">
          <nav aria-label="Breadcrumb" className="mb-6 flex flex-wrap items-center gap-2 text-sm text-mute">
            <AppLink href="/" className="transition-colors hover:text-bone">Home</AppLink>
            <span aria-hidden="true">/</span>
            <AppLink href="/brands" className="transition-colors hover:text-bone">Brands</AppLink>
            <span aria-hidden="true">/</span>
            <span className="text-bone/80">{brand.name}</span>
          </nav>

          {brand.logo ? (
            <img src={brand.logo} alt={brand.name} className="h-14 max-w-[70%] object-contain object-left md:h-20" />
          ) : (
            <h1 className="font-serif text-5xl leading-[0.98] tracking-tight md:text-7xl">{brand.name}</h1>
          )}
          {meta && <p className="mt-4 text-base text-mute md:text-lg">{meta}</p>}

          <dl className="mt-8 grid gap-px overflow-hidden rounded-2xl border border-line bg-line sm:grid-cols-3">
            {stats.map(([label, value]) => (
              <div key={label} className="bg-ink px-5 py-4">
                <dt className="text-xs text-mute">{label}</dt>
                <dd className="mt-1 font-mono text-sm text-bone">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </header>

      <section className="container-x pb-16 pt-10 md:pb-24 md:pt-14">
        <div className="mb-8 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
          <h2 className="font-serif text-3xl md:text-4xl">
            {guitars.length} {guitars.length === 1 ? 'guitar' : 'guitars'} by {brand.name}
          </h2>
          <Button href={brandCatalogUrl(brand.name)} variant="ghost">
            Filter in catalog
          </Button>
        </div>

        <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3 lg:gap-6">
          {guitars.map((g, i) => (
            <CatalogCard key={g.id} guitar={g} index={i} />
          ))}
        </div>
      </section>

      <section className="border-t border-line py-14 md:py-20">
        <div className="container-x">
          <h2 className="mb-6 font-serif text-3xl md:text-4xl">More brands</h2>
          <ul className="flex flex-wrap gap-2">
            {others.map((b) => (
              <li key={b.id}>
                <AppLink
                  href={brandUrl(b.name)}
                  className="inline-flex min-h-[44px] items-center gap-2 rounded-full border border-white/15 px-5 text-sm text-bone/85 transition duration-300 hover:border-gold hover:text-gold"
                >
                  {b.name}
                  <span className="font-mono text-xs text-mute">{b.models}</span>
                </AppLink>
              </li>
            ))}
          </ul>
        </div>
      </section>
    </>
  );
}

export default function BrandDetailPage() {
  const { id } = useParams();
  const brand = BRANDS_BY_ID[(id ?? '').toLowerCase()];
  if (!brand) return <NotFoundPage />;
  return <BrandContent key={brand.id} brand={brand} />;
}
