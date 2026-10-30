import { t } from '@/i18n';
import { CATEGORIES } from '@/data/categories';
import CategoryCard from './CategoryCard';

export default function Categories() {
  return (
    <section id="categories" className="signature-categories bg-ink" aria-labelledby="home-categories-title">
      <div className="container-x">
        <h2 id="home-categories-title" className="experience-category-heading">{t('cat.title')}</h2>
        <div className="signature-category-grid">
          {CATEGORIES.map((category) => <CategoryCard key={category.id} category={category} />)}
        </div>
      </div>
    </section>
  );
}
