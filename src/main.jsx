import React from 'react';
import ReactDOM from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import './styles/tokens.css';
import './index.css';
import './styles/polish.css';
import './styles/home-discovery.css';
import './styles/home-brands.css';
import './styles/brand-directory.css';
import './styles/home-experiences.css';
import CatalogUnavailable from './components/ui/CatalogUnavailable';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<div className="container-x py-24 text-mute" role="status">กำลังโหลด Fretline…</div>);
async function start() {
  try {
    let catalogUnavailable = false;
    // Load the published snapshot BEFORE modules compute brand/category/search
    // indexes. Refresh receives the latest publication without changing page UI.
    const { hydratePublishedCatalog, installPublishedCatalog } = await import('./features/admin/publicCatalog');
    try { await hydratePublishedCatalog(); }
    catch (error) {
      if (!['/admin', '/qr'].includes(window.location.pathname.replace(/\/$/, ''))) throw error;
      // Keep recovery/login accessible without exposing a stale static catalog.
      installPublishedCatalog([]);
      catalogUnavailable = true;
    }
    const { default: App } = await import('./App.jsx');
    root.render(<React.StrictMode><BrowserRouter><App catalogUnavailable={catalogUnavailable} /></BrowserRouter></React.StrictMode>);
  } catch {
    root.render(<main><CatalogUnavailable /></main>);
  }
}
start();
