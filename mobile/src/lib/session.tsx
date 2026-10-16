import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';
import type { Session } from '@supabase/supabase-js';
import { supabase } from './supabase';

const SessionContext = createContext<{ session: Session | null; loading: boolean }>({ session: null, loading: true });
export function SessionProvider({ children }: { children: ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(Boolean(supabase));
  useEffect(() => {
    if (!supabase) return;
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (mounted) { setSession(data.session); setLoading(false); }
    }).catch(() => { if (mounted) setLoading(false); });
    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, next) => {
      if (mounted) { setSession(next); setLoading(false); }
    });
    return () => { mounted = false; subscription.unsubscribe(); };
  }, []);
  return <SessionContext.Provider value={{ session, loading }}>{children}</SessionContext.Provider>;
}
export const useSession = () => useContext(SessionContext);
