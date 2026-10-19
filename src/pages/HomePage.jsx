import CompareSection from '@/components/compare/CompareSection';
import Brands from '@/components/home/Brands';
import Categories from '@/components/home/Categories';
import FeaturedGuitars from '@/components/home/FeaturedGuitars';
import FindMyGuitar from '@/components/home/FindMyGuitar';
import Hero from '@/components/home/Hero';

/** ลำดับ section ของหน้าแรก — สลับหรือเพิ่มได้ที่นี่ */
export default function HomePage() {
  return (
    <>
      <Hero />
      <Categories />
      <FeaturedGuitars />
      <Brands />
      <CompareSection />
      <FindMyGuitar />
    </>
  );
}
