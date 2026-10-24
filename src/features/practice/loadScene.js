import builtSceneUrl from 'virtual:fretline-practice-scene';

// Safari/WebKit can retain a rejected module URL even across a document reload.
// A retry uses a new URL for the self-contained scene/engine chunk. Successful
// factories are retained for context recovery and SPA navigation, never scenes.
const baseUrl = new URL(builtSceneUrl, import.meta.url).href;
const STORAGE_KEY = 'fretline:practice-module-recovery';
let revision = '';
let retryCount = 0;
let loadedModule = null;
try {
  const saved = JSON.parse(sessionStorage.getItem(STORAGE_KEY));
  if (saved?.buildUrl === baseUrl && typeof saved.revision === 'string') revision = saved.revision;
} catch { /* Private browsing/storage denial must not prevent practice. */ }

export function loadPracticeScene() {
  if (loadedModule) return Promise.resolve(loadedModule);
  const url = new URL(baseUrl);
  if (revision) url.searchParams.set('practice-retry', revision);
  return import(/* @vite-ignore */ url.href).then((module) => {
    loadedModule = module;
    try {
      if (revision) sessionStorage.setItem(STORAGE_KEY, JSON.stringify({ buildUrl: baseUrl, revision }));
      else sessionStorage.removeItem(STORAGE_KEY);
    } catch { /* In-memory recovery also works without storage. */ }
    return module;
  });
}

export function retryFailedSceneModule() {
  revision = `${Date.now()}-${++retryCount}`;
}
