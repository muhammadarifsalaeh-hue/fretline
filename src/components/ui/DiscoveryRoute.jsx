import { Component, Suspense } from 'react';
import { useLocation } from 'react-router-dom';
import { t } from '@/i18n';
import AppLink from './AppLink';

function LoadingState() {
  return (
    <section className="container-x min-h-[70svh] pb-16 pt-32" role="status" aria-busy="true" aria-label={t('discovery.loading')}>
      <p className="mb-6 text-sm text-gold">{t('discovery.loading')}</p>
      <div aria-hidden="true" className="grid grid-cols-2 gap-4 md:grid-cols-3">
        {Array.from({ length: 6 }, (_, i) => <div key={i} className="h-64 animate-pulse rounded-xl border border-line bg-surface motion-reduce:animate-none" />)}
      </div>
    </section>
  );
}

class DiscoveryBoundary extends Component {
  state = { failed: false };
  static getDerivedStateFromError() { return { failed: true }; }
  render() {
    if (!this.state.failed) return this.props.children;
    return (
      <section className="container-x min-h-[65svh] pb-20 pt-36">
        <div role="alert" className="rounded-xl border border-line bg-surface p-8">
          <h1 className="text-2xl font-medium">{t('discovery.errorTitle')}</h1>
          <p className="mt-3 text-sm text-mute">{t('discovery.errorText')}</p>
          <div className="mt-6 flex flex-wrap gap-5">
            <button type="button" onClick={() => window.location.reload()} className="min-h-11 rounded-lg bg-gold px-5 text-sm text-ink">{t('discovery.retry')}</button>
            <AppLink href="/" className="inline-flex min-h-11 items-center text-sm text-gold">{t('nav.home')}</AppLink>
          </div>
        </div>
      </section>
    );
  }
}

export default function DiscoveryRoute({ children }) {
  const { pathname } = useLocation();
  return <DiscoveryBoundary key={pathname}><Suspense fallback={<LoadingState />}>{children}</Suspense></DiscoveryBoundary>;
}
