import { useEffect } from 'react';
import { t } from '@/i18n';
import { GUITARS_BY_ID } from '@/data/guitars';
import IMAGE_RIGHTS from '@/data/catalog/imageRights.json';
import { hasImageRights } from '@/utils/imageRights';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import DiscoveryHeading from '@/components/ui/DiscoveryHeading';
import GuitarImage from '@/components/guitar/GuitarImage';
import ImageAttribution from '@/components/detail/ImageAttribution';

const photos = Object.entries(IMAGE_RIGHTS).flatMap(([id, entries]) => entries.filter((entry) => hasImageRights(entry, id)).map((rights) => ({ guitar: GUITARS_BY_ID[id], rights }))).filter((item) => item.guitar);
export default function ImageCreditsPage() {
  useEffect(() => { document.title = `${t('p6.images.title')} — Fretline`; }, []);
  return <div className="phase5-page image-credits-page">
    <DiscoveryHeading eyebrow="IMAGE SOURCES & LICENSES" title={t('p6.images.title')} description={t('p6.images.intro')}
      breadcrumbs={[{ label: t('p6.images.indexLink') }]} />
    <section className="container-x phase5-body">
      <p className="mb-5 text-sm text-gold">{t('p6.images.count', { n: photos.length })}</p>
      <ul className="grid gap-6">
        {photos.map(({ guitar, rights }) => <li key={`${guitar.id}/${rights.file}`} className="grid gap-6 rounded-lg border border-line bg-surface p-5 sm:grid-cols-[180px_1fr]">
          <GuitarImage guitar={guitar} className="aspect-[3/4] rounded-md" sizes="180px" />
          <div className="min-w-0">
            <h2 className="font-serif text-3xl">{guitar.brand} {guitar.name}</h2>
            <ImageAttribution image={{ attribution: rights }} />
            <p className="mt-3 text-xs leading-6 text-mute">{t('p6.images.model')}: {rights.modelMatchNote}</p>
            <p className="mt-2 text-xs text-mute">{t('p6.images.checked', { date: rights.checkedOn })}</p>
            <AppLink href={guitarUrl(guitar.slug)} className="phase4-button mt-5">{t('p6.images.viewModel')}</AppLink>
          </div>
        </li>)}
      </ul>
      <p className="phase5-note mt-6">{t('p6.images.assetOnly')} {t('p6.images.fallback')}</p>
    </section>
  </div>;
}
