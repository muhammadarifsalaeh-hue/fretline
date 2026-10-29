// A cached session or a browser flag never establishes administrator access.
// Both the identity and membership must be checked by Supabase on every check.
function bounded(request) {
  let timer;
  return Promise.race([
    Promise.resolve(request),
    new Promise((_, reject) => { timer = setTimeout(() => reject(new Error('Access check timed out')), 10000); }),
  ]).finally(() => clearTimeout(timer));
}

export async function verifyAdminAccess(client) {
  try {
    const identity = await bounded(client.auth.getUser());
    if (identity.error || !identity.data?.user?.id) return false;
    const membership = await bounded(client.rpc('fretline_is_admin'));
    return !membership.error && membership.data === true;
  } catch { return false; }
}

export function watchAdminAccess(client, onChange, target = window) {
  let stopped = false, revision = 0, deferred;
  async function check() {
    const current = ++revision;
    onChange(false);
    const allowed = await verifyAdminAccess(client);
    if (!stopped && current === revision) onChange(allowed);
  }
  function invalidate() { revision++; onChange(false); }
  const { data: { subscription } } = client.auth.onAuthStateChange((event) => {
    invalidate();
    clearTimeout(deferred);
    // Do not await another Supabase call inside its auth-state callback/lock.
    if (event !== 'SIGNED_OUT') deferred = setTimeout(check, 0);
  });
  const visibleCheck = () => { if (target.document.visibilityState === 'visible') check(); };
  target.addEventListener('focus', check);
  target.addEventListener('online', check);
  target.addEventListener('offline', invalidate);
  target.document.addEventListener('visibilitychange', visibleCheck);
  const interval = setInterval(visibleCheck, 60000);
  check();
  return () => {
    stopped = true; revision++; clearTimeout(deferred); clearInterval(interval);
    subscription.unsubscribe();
    target.removeEventListener('focus', check);
    target.removeEventListener('online', check);
    target.removeEventListener('offline', invalidate);
    target.document.removeEventListener('visibilitychange', visibleCheck);
  };
}
