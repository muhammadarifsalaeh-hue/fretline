import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import CategoryCard from './CategoryCard';

export default function Categories() {
  return (
    <section id="categories" className="signature-categories bg-ink" aria-labelledby="home-categories-title">
      <div className="container-x">
        <h2 id="home-categories-title" className="sr-only">{t('cat.title')}</h2>
        <p className="home-category-eyebrow" aria-hidden="true">EXPLORE BY CATEGORY</p>
        <div className="signature-category-grid">
          {CATEGORIES.map((category) => <CategoryCard key={category.id} category={category} />)}
        </div>
      </div>
    </section>
  );
}
