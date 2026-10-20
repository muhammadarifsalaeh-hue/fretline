import { t } from '@/i18n';
import { BRANDS, BRANDS_BY_ID, FEATURED_BRANDS } from '@/data/brands';
import { brandUrl } from '@/utils/routes';
import Reveal from '@/components/ui/Reveal';
import SectionHeading from '@/components/ui/SectionHeading';
import { ArrowRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import SmartImage from '@/components/ui/SmartImage';

/** โลโก้แบรนด์: ใช้รูป (ขาวโมโนโครม) ถ้ามี ไม่งั้นแสดงเป็นชื่อแบรนด์ */
function BrandMark({ brand, decorative = false }) {
  return (
    <AppLink
      href={brandUrl(brand.name)}
      tabIndex={decorative ? -1 : undefined}
      className="group relative flex shrink-0 flex-col items-center px-8 py-4 md:px-12"
      aria-label={`${brand.name}, ${t('unit.models', { n: brand.models })}`}
    >
      {brand.logo ? (
        <img src={brand.logo} alt={brand.name} className="h-9 opacity-50 transition-opacity duration-300 group-hover:opacity-100 md:h-11" />
      ) : (
        <span className="font-serif text-4xl text-bone/50 transition-colors duration-300 group-hover:text-bone md:text-5xl">
          {brand.name}
        </span>
      )}
      <span className="absolute -bottom-1 font-mono text-xs text-gold opacity-0 transition-opacity duration-300 group-hover:opacity-100">
        {t('unit.models', { n: brand.models })}
      </span>
    </AppLink>
  );
}

function FeaturedBrandCard({ feature }) {
  const brand = BRANDS_BY_ID[feature.id];
  return (
    <AppLink
      href={brandUrl(brand.name)}
      className="group relative block h-[380px] w-[82%] shrink-0 snap-start overflow-hidden rounded-3xl bg-surface ring-1 ring-white/5 sm:w-[55%] md:h-[440px] md:w-auto"
    >
      {feature.image ? (
        <SmartImage src={feature.image} alt={`${brand.name} guitars`} className="absolute inset-0" imgClassName="opacity-70 group-hover:scale-105 group-hover:opacity-90" />
      ) : (
        <div aria-hidden="true" className="absolute inset-0 overflow-hidden bg-gradient-to-br from-[#2a2a2a] via-[#181818] to-[#0f0f0f]">
          <div className="absolute inset-0 bg-[radial-gradient(60%_50%_at_30%_20%,rgba(200,161,90,0.12),transparent_70%)]" />
          <span className="absolute -right-3 top-4 select-none font-serif text-[7.5rem] leading-none tracking-tighter text-white/[0.05] transition-transform duration-700 ease-premium group-hover:-translate-x-2">
            {brand.name}
          </span>
        </div>
      )}
      <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-ink via-ink/50 to-ink/10" />
      <div className="absolute inset-x-7 bottom-7">
        <p className="font-mono text-xs text-bone/70">{t('p6.brand.sources', { n: brand.sourceModels })}</p>
        <h3 className="mt-2 font-serif text-5xl leading-none tracking-tight">{brand.name}</h3>
        <p className="mt-3 text-sm text-bone/70">{t('unit.models', { n: brand.models })}</p>
        <span className="mt-5 inline-flex items-center gap-2 text-sm text-gold">
          {t('brand.viewCollection')}
          <ArrowRightIcon size={16} className="transition-transform duration-300 ease-premium group-hover:translate-x-1" />
        </span>
      </div>
    </AppLink>
  );
}

export default function Brands() {
  return (
    <section id="brands" className="section-y overflow-hidden bg-ink">
      <div className="container-x">
        <Reveal>
          <SectionHeading title={t('brand.homeTitle')} action={{ label: t('brand.viewAll'), href: '/brands' }} />
        </Reveal>
      </div>

      {/* Marquee: เลื่อนช้า ๆ และหยุดเมื่อ hover (ซ้ำรายการ 2 ชุดเพื่อให้วนต่อเนื่อง) */}
      <Reveal delay={100}>
        <div className="mb-16 border-y border-line py-8 [mask-image:linear-gradient(to_right,transparent,black_12%,black_88%,transparent)] md:mb-20">
          <div className="flex w-max animate-marquee hover:[animation-play-state:paused]">
            {[...BRANDS, ...BRANDS].map((brand, i) => (
              <div key={`${brand.id}-${i}`} aria-hidden={i >= BRANDS.length}>
                <BrandMark brand={brand} decorative={i >= BRANDS.length} />
              </div>
            ))}
          </div>
        </div>
      </Reveal>

      <div className="container-x">
        <Reveal delay={150}>
          <div className="-mx-5 flex snap-x snap-mandatory gap-4 overflow-x-auto px-5 pb-2 [scrollbar-width:none] sm:-mx-8 sm:px-8 md:mx-0 md:grid md:grid-cols-3 md:gap-5 md:overflow-visible md:px-0 [&::-webkit-scrollbar]:hidden">
            {FEATURED_BRANDS.map((feature) => (
              <FeaturedBrandCard key={feature.id} feature={feature} />
            ))}
          </div>
        </Reveal>
      </div>
    </section>
  );
}
