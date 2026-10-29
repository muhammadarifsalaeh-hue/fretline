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

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<div className="container-x py-24 text-mute" role="status">กำลังโหลด Fretline…</div>);
async function start() {
  try {
    // Load the published snapshot BEFORE modules compute brand/category/search
    // indexes. Refresh receives the latest publication without changing page UI.
    const { hydratePublishedCatalog, installPublishedCatalog } = await import('./features/admin/publicCatalog');
    try { await hydratePublishedCatalog(); }
    catch (error) {
      if (!window.location.pathname.startsWith('/admin')) throw error;
      // Keep recovery/login accessible without exposing a stale static catalog.
      installPublishedCatalog([]);
    }
    const { default: App } = await import('./App.jsx');
    root.render(<React.StrictMode><BrowserRouter><App /></BrowserRouter></React.StrictMode>);
  } catch {
    root.render(<main className="container-x min-h-screen py-24" role="alert">
      <h1 className="text-2xl">โหลดข้อมูลกีตาร์ไม่สำเร็จ</h1>
      <p className="mt-4 text-mute">กรุณาตรวจการเชื่อมต่อแล้วลองอีกครั้ง</p>
      <button className="mt-6 min-h-12 rounded-lg bg-gold px-6 text-ink" onClick={() => window.location.reload()}>ลองอีกครั้ง</button>
      <a className="ml-6 inline-flex min-h-12 items-center text-gold" href="/admin">Admin Studio</a>
    </main>);
  }
}
start();
