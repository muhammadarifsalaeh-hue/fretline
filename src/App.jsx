import { Route, Routes } from 'react-router-dom';
import { ShopProvider } from '@/context/ShopContext';
import BottomBar from '@/components/layout/BottomBar';
import CompareBar from '@/components/layout/CompareBar';
import Footer from '@/components/layout/Footer';
import Navbar from '@/components/layout/Navbar';
import ScrollManager from '@/components/layout/ScrollManager';
import Toast from '@/components/layout/Toast';
import ComparePage from '@/pages/ComparePage';
import BrandDetailPage from '@/pages/BrandDetailPage';
import BrandsPage from '@/pages/BrandsPage';
import CatalogPage from '@/pages/CatalogPage';
import GuitarDetailPage from '@/pages/GuitarDetailPage';
import FindMyGuitarPage from '@/pages/FindMyGuitarPage';
import HomePage from '@/pages/HomePage';
import NotFoundPage from '@/pages/NotFoundPage';
import WishlistPage from '@/pages/WishlistPage';

export default function App() {
  return (
    <ShopProvider>
      <ScrollManager />
      <Navbar />
      {/* pb ด้านล่างเว้นที่ให้ BottomBar บนมือถือ */}
      <div className="pb-[64px] lg:pb-0">
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/guitars" element={<CatalogPage />} />
            <Route path="/brands" element={<BrandsPage />} />
            <Route path="/brands/:id" element={<BrandDetailPage />} />
            <Route path="/wishlist" element={<WishlistPage />} />
            <Route path="/compare" element={<ComparePage />} />
            <Route path="/find-my-guitar" element={<FindMyGuitarPage />} />
            <Route path="/guitars/:slug" element={<GuitarDetailPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </main>
        <Footer />
      </div>
      <CompareBar />
      <BottomBar />
      <Toast />
    </ShopProvider>
  );
}
