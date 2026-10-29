// Explicit canonical production URL only. Never derive a QR from location.origin:
// the current browser could be on Codespaces or a temporary Vercel preview.
export function productionSiteUrl(value = import.meta.env?.VITE_SITE_URL) {
  if (typeof value !== 'string' || !value.trim()) return null;
  try {
    const url = new URL(value.trim());
    const host = url.hostname.toLowerCase();
    if (url.protocol !== 'https:' || url.username || url.password || url.port || url.search || url.hash || url.pathname !== '/') return null;
    if (!/^[a-z0-9-]+(?:\.[a-z0-9-]+)+$/.test(host) || /^\d+(?:\.\d+){3}$/.test(host)) return null;
    if (['localhost', 'local', 'test', 'invalid', 'example', 'example.com', 'example.org', 'example.net', 'github.dev', 'app.github.dev', 'gitpod.io', 'ngrok-free.app', 'trycloudflare.com'].some(domain => host === domain || host.endsWith(`.${domain}`))) return null;
    return url.origin;
  } catch { return null; }
}
