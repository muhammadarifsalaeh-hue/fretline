import { useEffect } from 'react';
import { t } from '@/i18n';
import CompareSection from '@/components/compare/CompareSection';
import Brands from '@/components/home/Brands';
import Categories from '@/components/home/Categories';
import FeaturedGuitars from '@/components/home/FeaturedGuitars';
import FindMyGuitar from '@/components/home/FindMyGuitar';
import Hero from '@/components/home/Hero';
import '@/styles/home-premium.css';

/** ลำดับ section ของหน้าแรก — สลับหรือเพิ่มได้ที่นี่ */
export default function HomePage() {
  useEffect(() => { document.title = t('home.docTitle'); }, []);
  return (
    <div className="signature-home premium-home">
      <Hero />
      <Brands />
      <Categories />
      <div className="home-editorial-pair container-x">
        <FindMyGuitar />
        <CompareSection />
      </div>
      <FeaturedGuitars />
    </div>
  );
}
