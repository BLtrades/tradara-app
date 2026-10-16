import 'react-native-url-polyfill/auto';
import 'expo-sqlite/localStorage/install';
import { AppState } from 'react-native';
import { createClient } from '@supabase/supabase-js';

// Publishable keys are intended for client applications. RLS protects user data.
// Environment variables can point local builds at a separate test project.
const url = process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://lxrjawzqfqrnswrjxovk.supabase.co';
const key = process.env.EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY || process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'sb_publishable_ddJGlAsCJ86PVJQmKYxvLA_6FrjoB9b';
export const configured = Boolean(url && key);
export const supabase = configured ? createClient(url!, key!, {
  auth: { storage: localStorage, autoRefreshToken: true, persistSession: true, detectSessionInUrl: false },
}) : null;

if (supabase) AppState.addEventListener('change', state => {
  if (state === 'active') supabase.auth.startAutoRefresh();
  else supabase.auth.stopAutoRefresh();
});
