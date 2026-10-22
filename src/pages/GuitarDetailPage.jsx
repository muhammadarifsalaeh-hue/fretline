import { t } from '@/i18n';
import { useEffect, useRef, useState } from 'react';
import { useParams } from 'react-router-dom';
import ColorSwatches from '@/components/detail/ColorSwatches';
import DataStatusNote from '@/components/detail/DataStatusNote';
import DetailTabs from '@/components/detail/DetailTabs';
import GuitarGallery from '@/components/detail/GuitarGallery';
import SimilarGuitars from '@/components/detail/SimilarGuitars';
import StickyGuitarBar from '@/components/detail/StickyGuitarBar';
import AppLink from '@/components/ui/AppLink';
import { CheckIcon, CompareIcon, HeartIcon } from '@/components/ui/Icons';
import { CATEGORIES } from '@/data/categories';
import { SAVED_GUITARS_BY_ID } from '@/data/guitars';
import { MAX_COMPARE, useShop } from '@/context/ShopContext';
import { cn } from '@/utils/cn';
import { NOT_SPECIFIED, formatKg, formatPrice, formatScale } from '@/utils/format';
import { brandUrl, categoryUrl } from '@/utils/routes';
import NotFoundPage from './NotFoundPage';
import PriceSourceNote from '@/components/guitar/PriceSourceNote';
import { hasManufacturerRrp } from '@/utils/dataTrust';
import useDevelopmentImagePreview from '@/hooks/useDevelopmentImagePreview';
import LocalPreviewImagePicker from '@/components/guitar/LocalPreviewImagePicker';

const firstSentence = (text = '') => {
  const paragraph = text.split('\n\n')[0];
  return paragraph.includes('. ') ? `${paragraph.split('. ')[0]}.` : paragraph;
};

function DetailContent({ guitar }) {
  const { compare, wishlist, toggleCompare, toggleWishlist } = useShop();
  const [selectionIndex, setSelectionIndex] = useState(0);
  const developmentPreview = useDevelopmentImagePreview(guitar);
  const galleryImages = developmentPreview?.images ?? guitar.gallery;
  const imageColors = developmentPreview?.colors ?? guitar.gallery.flatMap((image) => image.color ? [{ ...image.color, imageId: image.id }] : []);
  const hasImageColors = imageColors.length > 0;
  const colors = hasImageColors ? imageColors : guitar.colors;
  const colorIndex = hasImageColors
    ? colors.findIndex((color) => color.imageId === galleryImages[selectionIndex]?.id)
    : selectionIndex;
  const selectColor = (index) => setSelectionIndex(hasImageColors
    ? galleryImages.findIndex((image) => image.id === colors[index].imageId)
    : index);
  const gallery = <GuitarGallery guitar={guitar} activeIndex={hasImageColors ? selectionIndex : undefined} onIndexChange={hasImageColors ? setSelectionIndex : undefined} />;
  const [stuck, setStuck] = useState(false);
  const ctaRef = useRef(null);
  const inCompare = compare.includes(guitar.id);
  const compareFull = !inCompare && compare.length >= MAX_COMPARE;
  const inWishlist = wishlist.includes(guitar.id);
  const categoryName = CATEGORIES.find((category) => category.id === guitar.category)?.name;
  const sample = guitar.dataStatus === 'sample';

  useEffect(() => { document.title = `${guitar.brand} ${guitar.name} — Fretline`; }, [guitar]);
  useEffect(() => {
    if (!ctaRef.current || !('IntersectionObserver' in window)) return undefined;
    const observer = new IntersectionObserver(([entry]) => setStuck(!entry.isIntersecting && entry.boundingClientRect.top < 0));
    observer.observe(ctaRef.current);
    return () => observer.disconnect();
  }, []);

  const keyFeatures = [
    { label: t('detail.tone'), value: guitar.specs.pickups ?? NOT_SPECIFIED },
    { label: t('detail.feel'), value: [(guitar.specs.scale != null || guitar.specs.scaleMm != null) && `${t('row.scale')} ${formatScale(guitar.specs)}`, guitar.specs.frets != null && t('detail.fretsTxt', { n: guitar.specs.frets })].filter(Boolean).join(', ') || NOT_SPECIFIED },
    { label: t('detail.build'), value: guitar.specs.body ?? NOT_SPECIFIED },
  ];

  return (
    <div className="detail-page discovery-page">
      {guitar.archived && <div className="container-x pt-6"><p className="archive-notice" role="note">{t('p7.archive.detail')} <AppLink href="/guitars" className="text-gold underline">{t('p7.archive.browse')}</AppLink></p></div>}
      <StickyGuitarBar guitar={guitar} visible={stuck} inCompare={inCompare} full={compareFull} onToggleCompare={() => toggleCompare(guitar)} />
      <section className="detail-hero container-x">
        <nav aria-label={t('common.breadcrumb')} className="discovery-breadcrumb">
          <AppLink href="/">{t('nav.home')}</AppLink><span aria-hidden="true">›</span>
          <AppLink href="/guitars">{t('nav.guitars')}</AppLink><span aria-hidden="true">›</span>
          <AppLink href={categoryUrl(guitar.category)}>{categoryName}</AppLink><span aria-hidden="true">›</span>
          <span className="text-bone/80">{guitar.brand} {guitar.name}</span>
        </nav>
        <div className="detail-main-grid">
          {developmentPreview ? <div>
            {gallery}
            <LocalPreviewImagePicker guitar={guitar} onApply={() => setSelectionIndex(0)} />
          </div> : gallery}
          <div className="detail-summary">
            <AppLink href={brandUrl(guitar.brand)} className="discovery-kicker hover:text-gold">{guitar.brand}</AppLink>
            <h1 className="mt-2 font-serif text-[clamp(2rem,3.7vw,3.5rem)]">{guitar.name}</h1>
            <div className="mt-3 flex flex-wrap gap-2">
              <AppLink href={categoryUrl(guitar.category)} className="detail-pill">{categoryName}</AppLink>
              <span className="detail-pill text-gold">{t(`status.${guitar.dataStatus ?? 'sample'}`)}</span>
            </div>
            <div className="detail-price-block">
              {sample && <p className="mb-1 text-xs text-gold">{t('detail.samplePrice')}</p>}
              <p className="flex flex-wrap items-baseline gap-3">
                <span className="font-mono text-3xl text-bone">{formatPrice(guitar.price)}</span>
                {guitar.oldPrice && <span className="font-mono text-sm text-mute line-through">{formatPrice(guitar.oldPrice)}</span>}
              </p>
              {hasManufacturerRrp(guitar) ? <PriceSourceNote guitar={guitar} full /> : <p className="mt-2 text-xs leading-6 text-mute">{guitar.price == null ? t('detail.noPrice') : t('detail.priceNote')}</p>}
            </div>
            <p className="mt-4 text-sm leading-7 text-bone/75">{firstSentence(guitar.description)}</p>
            {hasImageColors && galleryImages.length > 0 && <div className="gallery-color-selector preview-color-selector mt-6 border-t border-line pt-5">
              <ColorSwatches colors={colors} value={colorIndex} onChange={selectColor} allowNone
                emptyLabel={t('imagePreview.allColors')} label={t('artwork.color')} ariaLabel={t('artwork.chooseColor')} />
              {developmentPreview && <p className="mt-3 text-[11px] leading-5 text-mute">{t('imagePreview.colorNote')}</p>}
            </div>}
            <div className="detail-source-note mt-4"><DataStatusNote guitar={guitar} /></div>
            <div ref={ctaRef} className="detail-actions">
              <button type="button" onClick={() => toggleCompare(guitar)} disabled={compareFull} title={compareFull ? t('p4.compare.fullNote') : undefined} aria-pressed={inCompare} className={cn('detail-action disabled:cursor-not-allowed disabled:opacity-50', inCompare && 'is-active')}>
                {inCompare ? <CheckIcon size={18} /> : <CompareIcon size={18} />}{inCompare ? t('detail.added') : t('detail.add')}
              </button>
              <button type="button" onClick={() => toggleWishlist(guitar)} aria-pressed={inWishlist} className={cn('detail-action', inWishlist && 'is-active')}>
                <HeartIcon size={18} fill={inWishlist ? 'currentColor' : 'none'} />{inWishlist ? t('detail.saved') : t('detail.saveBtn')}
              </button>
            </div>
            {compareFull && <p className="mt-3 text-xs leading-6 text-gold" role="status">{t('p4.compare.fullNote')} <AppLink href="/compare" className="inline-flex min-h-11 items-center underline underline-offset-4">{t('detail.viewComparison', { n: compare.length })}</AppLink></p>}
            {inCompare && <AppLink href="/compare" className="mt-3 inline-flex min-h-11 items-center text-xs text-gold">{t('detail.viewComparison', { n: compare.length })}</AppLink>}
            <dl className="detail-facts">
              {[[t('filter.type'), categoryName], [t('row.strings'), guitar.specs.strings ?? NOT_SPECIFIED], [t('row.weight'), formatKg(guitar.specs.weightKg)]].map(([label, value]) => (
                <div key={label}><dt>{label}</dt><dd>{value}</dd></div>
              ))}
            </dl>
            {!hasImageColors && <ColorSwatches colors={colors} value={colorIndex} onChange={selectColor} />}
          </div>
        </div>
      </section>
      <DetailTabs guitar={guitar} keyFeatures={keyFeatures} />
      <SimilarGuitars guitar={guitar} />
    </div>
  );
}

export default function GuitarDetailPage() {
  const { slug } = useParams();
  const guitar = SAVED_GUITARS_BY_ID[slug];
  return guitar ? <DetailContent key={guitar.id} guitar={guitar} /> : <NotFoundPage />;
}
