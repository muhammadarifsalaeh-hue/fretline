const STORAGE_KEY = 'fretline:public-supabase-config';
export function validateConnection(url, key) {
  let parsed;
  try { parsed = new URL(url); } catch { return 'Project URL ไม่ถูกต้อง'; }
  if (parsed.protocol !== 'https:' || !/^[a-z0-9-]+\.supabase\.co$/.test(parsed.hostname) || parsed.pathname !== '/' || parsed.search || parsed.hash || parsed.username || parsed.password) return 'ใช้ Project URL จาก Supabase เช่น https://project.supabase.co';
  if (!/^sb_publishable_[A-Za-z0-9_-]+$/.test(key)) return 'ใช้ Publishable key ที่ขึ้นต้น sb_publishable_ เท่านั้น ห้ามใช้ Secret key';
  return null;
}
export function readConnection() {
  const env = import.meta.env ?? {};
  if (env.VITE_SUPABASE_URL || env.VITE_SUPABASE_PUBLISHABLE_KEY) {
    const config = { url: (env.VITE_SUPABASE_URL ?? '').trim(), key: (env.VITE_SUPABASE_PUBLISHABLE_KEY ?? '').trim(), deployed: true };
    return validateConnection(config.url, config.key) ? null : config;
  }
  try {
    const config = JSON.parse(localStorage.getItem(STORAGE_KEY));
    return config && !validateConnection(config.url, config.key) ? { ...config, deployed: false } : null;
  } catch { return null; }
}
export function saveConnection(url, key) {
  const error = validateConnection(url.trim(), key.trim());
  if (error) throw new Error(error);
  localStorage.setItem(STORAGE_KEY, JSON.stringify({ url: url.trim().replace(/\/$/, ''), key: key.trim() }));
}
export function clearConnection() { localStorage.removeItem(STORAGE_KEY);sessionStorage.removeItem('fretline:remote-preview'); }
export function remoteCatalogEnabled() {
  if(import.meta.env?.VITE_CATALOG_SOURCE==='supabase')return true;
  const requested=typeof location!=='undefined' && new URLSearchParams(location.search).get('fretline-preview')==='1';
  try{
    if(requested)sessionStorage.setItem('fretline:remote-preview','1');
    return requested||sessionStorage.getItem('fretline:remote-preview')==='1';
  }catch{return requested;}
}
let singleton;
export async function getSupabase() {
  const config = readConnection();
  if (!config) throw new Error('ยังไม่ได้ตั้งค่าการเชื่อมต่อ Supabase');
  if (!singleton || singleton.url !== config.url || singleton.key !== config.key) {
    const { createClient } = await import('@supabase/supabase-js');
    singleton = { ...config, client: createClient(config.url, config.key, { auth: { persistSession: true, autoRefreshToken: true, detectSessionInUrl: true, flowType: 'pkce' } }) };
  }
  return singleton.client;
}
