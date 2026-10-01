import { Stack, type ErrorBoundaryProps } from 'expo-router';
import { SessionProvider, useSession } from '../lib/session';
import { Button, Heading, Loading, Page, colors } from '../components/ui';

function ScreenErrorBoundary({ retry }: ErrorBoundaryProps) {
  return <Page>
    <Heading subtitle="Your account and saved data are safe. Try loading this screen again.">Something went wrong</Heading>
    <Button title="Try again" onPress={() => { void retry(); }} />
  </Page>;
}

export const unstable_settings = { screenErrorBoundary: ScreenErrorBoundary };
export function SuspenseFallback() { return <Loading />; }

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
