import { t } from '@/i18n';
import { ChevronLeftIcon, ChevronRightIcon } from '@/components/ui/Icons';

export default function CatalogPagination({ page, pageCount, total, pageSize, onPage }) {
  const from = (page - 1) * pageSize + 1;
  const to = Math.min(page * pageSize, total);
  const pages = Array.from({ length: pageCount }, (_, i) => i + 1)
    .filter((value) => value === 1 || value === pageCount || Math.abs(value - page) <= 1);
  return (
    <div className="catalog-pagination">
      <p className="text-xs text-mute" aria-live="polite">{t('catalog.pageRange', { from, to, total })}</p>
      <nav aria-label={t('catalog.pagination')} className="flex flex-wrap justify-center gap-1.5">
        <button type="button" disabled={page === 1} aria-label={t('catalog.prevPage')} onClick={() => onPage(page - 1)}><ChevronLeftIcon size={16} /></button>
        {pages.map((value, index) => (
          <span key={value} className="contents">
            {index > 0 && value - pages[index - 1] > 1 && <span aria-hidden="true" className="grid w-7 place-items-center text-mute">…</span>}
            <button type="button" aria-current={page === value ? 'page' : undefined}
              aria-label={t('catalog.pageNumber', { n: value })} onClick={() => onPage(value)}>{value}</button>
          </span>
        ))}
        <button type="button" disabled={page === pageCount} aria-label={t('catalog.nextPage')} onClick={() => onPage(page + 1)}><ChevronRightIcon size={16} /></button>
      </nav>
    </div>
  );
}
