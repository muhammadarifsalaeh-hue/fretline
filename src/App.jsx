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
import { t } from '@/i18n';

const BrandsPage = lazy(() => import('@/pages/BrandsPage'));
const BrandDetailPage = lazy(() => import('@/pages/BrandDetailPage'));
const WishlistPage = lazy(() => import('@/pages/WishlistPage'));
const ImageCreditsPage = lazy(() => import('@/pages/ImageCreditsPage'));

const ComparePage = lazy(() => import('@/pages/ComparePage'));
const FindMyGuitarPage = lazy(() => import('@/pages/FindMyGuitarPage'));
const CatalogPage = lazy(() => import('@/pages/CatalogPage'));
const GuitarDetailPage = lazy(() => import('@/pages/GuitarDetailPage'));
const PracticePage = lazy(() => import('@/pages/PracticePage'));
const AdminStudioPage = lazy(() => import('@/pages/AdminStudioPage'));

export default function App() {
  return (
    <ShopProvider>
      <a href="#main-content" className="skip-link">{t('a11y.skip')}</a>
      <ScrollManager />
      <Navbar />
      {/* pb ด้านล่างเว้นที่ให้ BottomBar บนมือถือ */}
      <div className="app-content">
        <main id="main-content" tabIndex={-1}>
          <Routes>
            <Route path="/" element={<DiscoveryRoute><HomePage /></DiscoveryRoute>} />
            <Route path="/guitars" element={<DiscoveryRoute><CatalogPage /></DiscoveryRoute>} />
            <Route path="/brands" element={<DiscoveryRoute><BrandsPage /></DiscoveryRoute>} />
            <Route path="/brands/:id" element={<DiscoveryRoute><BrandDetailPage /></DiscoveryRoute>} />
            <Route path="/wishlist" element={<DiscoveryRoute><WishlistPage /></DiscoveryRoute>} />
            <Route path="/image-credits" element={<DiscoveryRoute><ImageCreditsPage /></DiscoveryRoute>} />
            <Route path="/compare" element={<DiscoveryRoute><ComparePage /></DiscoveryRoute>} />
            <Route path="/find-my-guitar" element={<DiscoveryRoute><FindMyGuitarPage /></DiscoveryRoute>} />
            <Route path="/practice" element={<DiscoveryRoute><PracticePage /></DiscoveryRoute>} />
            <Route path="/admin" element={<DiscoveryRoute><AdminStudioPage /></DiscoveryRoute>} />
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
