import { lazy } from 'react';
import DiscoveryRoute from '@/components/ui/DiscoveryRoute';
import { Route, Routes } from 'react-router-dom';
import { ShopProvider } from '@/context/ShopContext';
import BottomBar from '@/components/layout/BottomBar';
import CompareBar from '@/components/layout/CompareBar';
import Footer from '@/components/layout/Footer';
import Navbar from '@/components/layout/Navbar';
import ScrollManager from '@/components/layout/ScrollManager';
import Toast from '@/components/layout/Toast';
import HomePage from '@/pages/HomePage';
import NotFoundPage from '@/pages/NotFoundPage';

const BrandsPage = lazy(() => import('@/pages/BrandsPage'));
const BrandDetailPage = lazy(() => import('@/pages/BrandDetailPage'));
const WishlistPage = lazy(() => import('@/pages/WishlistPage'));

const ComparePage = lazy(() => import('@/pages/ComparePage'));
const FindMyGuitarPage = lazy(() => import('@/pages/FindMyGuitarPage'));
const CatalogPage = lazy(() => import('@/pages/CatalogPage'));
const GuitarDetailPage = lazy(() => import('@/pages/GuitarDetailPage'));

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
            <Route path="/guitars" element={<DiscoveryRoute><CatalogPage /></DiscoveryRoute>} />
            <Route path="/brands" element={<DiscoveryRoute><BrandsPage /></DiscoveryRoute>} />
            <Route path="/brands/:id" element={<DiscoveryRoute><BrandDetailPage /></DiscoveryRoute>} />
            <Route path="/wishlist" element={<DiscoveryRoute><WishlistPage /></DiscoveryRoute>} />
            <Route path="/compare" element={<DiscoveryRoute><ComparePage /></DiscoveryRoute>} />
            <Route path="/find-my-guitar" element={<DiscoveryRoute><FindMyGuitarPage /></DiscoveryRoute>} />
            <Route path="/guitars/:slug" element={<DiscoveryRoute><GuitarDetailPage /></DiscoveryRoute>} />
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
