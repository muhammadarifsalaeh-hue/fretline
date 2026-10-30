import { useEffect } from 'react';
import { t } from '@/i18n';
import CompareSection from '@/components/compare/CompareSection';
import Brands from '@/components/home/Brands';
import Categories from '@/components/home/Categories';
import FeaturedGuitars from '@/components/home/FeaturedGuitars';
import FindMyGuitar from '@/components/home/FindMyGuitar';
import Hero from '@/components/home/Hero';
import GuitarPracticeCard from '@/components/home/GuitarPracticeCard';
import '@/styles/home-premium.css';
import '@/styles/home-feature-restoration.css';
import '@/styles/home-targeted-refinement.css';

/** ลำดับ section ของหน้าแรก — สลับหรือเพิ่มได้ที่นี่ */
export default function HomePage() {
  useEffect(() => { document.title = t('home.docTitle'); }, []);
  return (
    <div className="signature-home premium-home">
      <Hero />
      <Brands />
      <Categories />
      <section id="home-features" className="home-feature-grid container-x" aria-label={t('nav.practice')}>
        <GuitarPracticeCard />
        <FindMyGuitar />
        <CompareSection />
      </section>
      <FeaturedGuitars />
    </div>
  );
}
