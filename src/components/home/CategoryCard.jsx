import { t } from '@/i18n';
import { cn } from '@/utils/cn';
import { categoryUrl } from '@/utils/routes';
import { ArrowUpRightIcon } from '@/components/ui/Icons';
import AppLink from '@/components/ui/AppLink';
import ArtBackdrop from '@/components/ui/ArtBackdrop';
import SmartImage from '@/components/ui/SmartImage';

export default function CategoryCard({ category, large = false, className = '' }) {
  return (
    <AppLink
      href={categoryUrl(category.id)}
      className={cn('group relative block overflow-hidden rounded-3xl bg-surface ring-1 ring-white/5', className)}
    >
      {category.image ? (
        <SmartImage
          src={category.image}
          alt={`${category.name} guitars`}
          className="absolute inset-0"
          imgClassName="group-hover:scale-[1.06] group-hover:-rotate-1"
        />
      ) : (
        <ArtBackdrop type={category.id} />
      )}
      <div aria-hidden="true" className="absolute inset-0 bg-gradient-to-t from-ink/90 via-ink/15 to-transparent transition-opacity duration-500 group-hover:opacity-80" />

      <span className="absolute right-5 top-5 grid h-11 w-11 place-items-center rounded-full border border-white/25 bg-ink/40 text-bone backdrop-blur-md transition duration-500 ease-premium group-hover:rotate-45 group-hover:border-gold group-hover:text-gold">
        <ArrowUpRightIcon size={18} />
      </span>

      <div className="absolute inset-x-6 bottom-6">
        <h3 className={cn('font-sans font-medium leading-none tracking-tight', large ? 'text-4xl md:text-5xl' : 'text-3xl')}>
          {category.name}
        </h3>
        <p className="mt-2 font-mono text-xs text-bone/70">{t('unit.models', { n: category.count })}</p>
      </div>
    </AppLink>
  );
}
