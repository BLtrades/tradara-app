import { Tabs } from 'expo-router';
import { colors } from '../../components/ui';
export default function Layout() { return <Tabs screenOptions={{ tabBarActiveTintColor: colors.accent, tabBarInactiveTintColor: colors.muted, tabBarStyle: { backgroundColor: colors.bg, borderTopColor: colors.border, height: 62 }, headerStyle: { backgroundColor: colors.bg }, headerTintColor: colors.text }}>
  <Tabs.Screen name="index" options={{ title: 'Radar' }} />
  <Tabs.Screen name="pipeline" options={{ title: 'Pipeline' }} />
  <Tabs.Screen name="insights" options={{ title: 'Insights' }} />
  <Tabs.Screen name="profile" options={{ title: 'Profile' }} />
  <Tabs.Screen name="settings" options={{ title: 'Settings' }} />
</Tabs>; }
