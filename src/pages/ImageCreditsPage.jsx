import { useEffect } from 'react';
import { t } from '@/i18n';
import { GUITARS_BY_ID } from '@/data/guitars';
import IMAGE_RIGHTS from '@/data/catalog/imageRights.json';
import PROJECT_ARTWORK from '@/data/catalog/projectArtwork.json';
import { hasImageRights } from '@/utils/imageRights';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import DiscoveryHeading from '@/components/ui/DiscoveryHeading';
import GuitarImage from '@/components/guitar/GuitarImage';
import { modelMatchDisplay } from '@/components/detail/imageDisplayCopy';
import ImageAttribution from '@/components/detail/ImageAttribution';
import DiscoveryPhotographyCredits from '@/components/detail/DiscoveryPhotographyCredits';
import HomePhotographyCredits from '@/components/detail/HomePhotographyCredits';

const photos = Object.entries(IMAGE_RIGHTS).flatMap(([id, entries]) => entries.filter((entry) => hasImageRights(entry, id)).map((rights) => ({ guitar: GUITARS_BY_ID[id], rights }))).filter((item) => item.guitar);
const artworks = Object.keys(PROJECT_ARTWORK).map((id) => GUITARS_BY_ID[id]).filter(Boolean);
export default function ImageCreditsPage() {
  useEffect(() => { document.title = `${t('p6.images.title')} — Fretline`; }, []);
  return <div className="phase5-page image-credits-page">
    <DiscoveryHeading eyebrow={t('targeted.credits.kicker')} title={t('p6.images.title')} description={t('p6.images.intro')}
      breadcrumbs={[{ label: t('p6.images.indexLink') }]} />
    <section className="container-x phase5-body">
      <p className="mb-5 text-sm text-gold">{t('p6.images.count', { n: photos.length })}</p>
      <ul className="grid gap-6">
        {photos.map(({ guitar, rights }) => <li key={`${guitar.id}/${rights.file}`} className="grid gap-6 rounded-lg border border-line bg-surface p-5 sm:grid-cols-[180px_1fr]">
          <GuitarImage guitar={guitar} className="aspect-square rounded-md" sizes="180px" />
          <div className="min-w-0">
            <h2 className="font-serif text-3xl">{guitar.brand} {guitar.name}</h2>
            <ImageAttribution image={{ attribution: rights }} />
            <p className="mt-3 text-xs leading-6 text-mute">{t('p6.images.model')}: {modelMatchDisplay(rights.modelMatchNote)}</p>
            <p className="mt-2 text-xs text-mute">{t('p6.images.checked', { date: rights.checkedOn })}</p>
            <AppLink href={guitarUrl(guitar.slug)} className="phase4-button mt-5">{t('p6.images.viewModel')}</AppLink>
          </div>
        </li>)}
      </ul>
      {artworks.length > 0 && <section className="mt-8" aria-labelledby="project-artwork-title">
        <h2 id="project-artwork-title" className="mb-5 font-serif text-2xl">{t('artwork.title')}</h2>
        {artworks.map((guitar) => <div key={guitar.id} className="grid gap-6 rounded-lg border border-line bg-surface p-5 sm:grid-cols-[180px_1fr]">
          <GuitarImage guitar={guitar} className="aspect-square rounded-md" sizes="180px" />
          <div className="min-w-0">
            <h3 className="font-serif text-3xl">{guitar.brand} {guitar.name}</h3>
            <details className="image-attribution mt-3 text-xs leading-6 text-mute"><summary>{t('artwork.details')}</summary><p>{t('targeted.artwork.provenance')}</p></details>
            <AppLink href={guitarUrl(guitar.slug)} className="phase4-button mt-5">{t('p6.images.viewModel')}</AppLink>
          </div>
        </div>)}
      </section>}
      <DiscoveryPhotographyCredits />
      <HomePhotographyCredits />
      <p className="phase5-note mt-6">{t('p6.images.assetOnly')} {t('p6.images.fallback')}</p>
    </section>
  </div>;
}
