import { createContext, useContext, useEffect, useState } from 'react';
import { getSupabase, readConnection } from '@/features/admin/config';
import { watchAdminAccess } from '@/features/admin/verifiedAccess';

const AdminAccessContext = createContext(false);
export const useAdminAccess = () => useContext(AdminAccessContext);

export function AdminAccessProvider({ children }) {
  const [allowed, setAllowed] = useState(false);
  useEffect(() => {
    if (!readConnection()) return undefined;
    let alive = true, stop;
    getSupabase().then(client => {
      if (alive) stop = watchAdminAccess(client, setAllowed);
    }).catch(() => { if (alive) setAllowed(false); });
    return () => { alive = false; stop?.(); };
  }, []);
  return <AdminAccessContext.Provider value={allowed}>{children}</AdminAccessContext.Provider>;
}
