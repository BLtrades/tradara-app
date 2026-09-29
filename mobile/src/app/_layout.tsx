import { Stack } from 'expo-router';
import { SessionProvider, useSession } from '../lib/session';
import { Loading, colors } from '../components/ui';

function Routes() {
  const { session, loading } = useSession();
  if (loading) return <Loading />;
  return <Stack screenOptions={{ headerStyle: { backgroundColor: colors.bg }, headerTintColor: colors.text, contentStyle: { backgroundColor: colors.bg } }}>
    <Stack.Screen name="reset-password" options={{ title: 'Reset password' }} />
    <Stack.Protected guard={!session}><Stack.Screen name="sign-in" options={{ headerShown: false }} /></Stack.Protected>
    <Stack.Protected guard={!!session}><Stack.Screen name="(tabs)" options={{ headerShown: false }} /></Stack.Protected>
  </Stack>;
}
export default function Layout() { return <SessionProvider><Routes /></SessionProvider>; }
