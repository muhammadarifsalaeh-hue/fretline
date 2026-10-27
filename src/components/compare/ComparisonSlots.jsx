import { LANG, t } from '@/i18n';
import { MAX_COMPARE } from '@/context/ShopContext';
import { publicPrice, trustedPrice } from '@/utils/dataTrust';
import { guitarUrl } from '@/utils/routes';
import AppLink from '@/components/ui/AppLink';
import GuitarImage from '@/components/guitar/GuitarImage';
import PriceSourceNote from '@/components/guitar/PriceSourceNote';
import { CloseIcon, PlusIcon } from '@/components/ui/Icons';

/** Product imagery is always resolved by the selected model ID, never the hero photo. */
export default function ComparisonSlots({ selected, onAdd, onRemove }) {
  return <ul className="pc-selection-grid" aria-label={LANG === 'en' ? 'Selected guitars' : 'กีตาร์ที่เลือกเปรียบเทียบ'}>
    {Array.from({ length: MAX_COMPARE }, (_, index) => {
      const guitar = selected[index];
      return guitar ? <li key={guitar.id} className="pc-model-card" data-comparison-slot={guitar.id} data-compare-card={guitar.id}>
        <AppLink href={guitarUrl(guitar.slug)} className="pc-model-card__image" aria-label={t('cmp.viewAria', { name: `${guitar.brand} ${guitar.name}` })}>
          <GuitarImage guitar={guitar} priority={index < 2} sizes="(min-width: 1024px) 23vw, (min-width: 600px) 24vw, 46vw" className="absolute inset-0" />
        </AppLink>
        <button type="button" data-compare-remove={guitar.id} onClick={() => onRemove(guitar.id)} aria-label={t('cmp.removeAria', { name: guitar.name })} className="pc-model-card__remove"><CloseIcon size={18} /></button>
        <div className="pc-model-card__copy">
          <p className="pc-model-card__brand">{guitar.brand}</p>
          <h2><AppLink href={guitarUrl(guitar.slug)}>{guitar.name}</AppLink></h2>
          <p className="pc-model-card__price">{trustedPrice(guitar) == null ? (LANG === 'en' ? 'Unconfirmed' : 'ยังไม่ยืนยัน') : publicPrice(guitar)}</p>
          <PriceSourceNote guitar={guitar} />
          {guitar.archived && <p className="archive-label">{t('p7.archive.label')}</p>}
        </div>
      </li> : <li key={`empty-${index}`} className="pc-empty-slot" data-compare-empty-slot={index + 1}>
        <button type="button" onClick={onAdd} aria-label={`${t('p4.compare.add')} ${index + 1}`}>
          <span className="pc-empty-slot__plus"><PlusIcon size={26} /></span>
          <span className="pc-empty-slot__title">{t('p4.compare.add')}</span>
          <span className="pc-empty-slot__hint">{LANG === 'en' ? `Choose up to ${MAX_COMPARE} models` : `เลือกได้สูงสุด ${MAX_COMPARE} รุ่น`}</span>
        </button>
      </li>;
    })}
  </ul>;
}
