import { useState } from 'react';
import { Alert, Text } from 'react-native';
import { Button, Field, Heading, Message, Page, styles } from '../../components/ui';
import { supabase } from '../../lib/supabase';
import { useSession } from '../../lib/session';

export default function Settings() {
  const { session } = useSession(); const [password, setPassword] = useState(''); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  async function changePassword() {
    if (!supabase) return;
    setBusy(true); const { error } = await supabase.auth.updateUser({ password });
    setMessage(error?.message ?? 'Password updated.'); if (!error) setPassword(''); setBusy(false);
  }
  function deleteAccount() { Alert.alert('Delete account permanently?', 'Your profile and pipeline will be removed. This cannot be undone.', [
    { text: 'Cancel', style: 'cancel' }, { text: 'Delete account', style: 'destructive', onPress: async () => {
      if (!supabase) return;
      setBusy(true); const { error } = await supabase.rpc('delete_my_account');
      if (error) setMessage(error.message); else await supabase.auth.signOut(); setBusy(false);
    } },
  ]); }
  return <Page><Heading subtitle="Manage your account and privacy.">Settings</Heading>
    <Text style={styles.muted}>Signed in as {session?.user.email}</Text>
    <Field label="New password" value={password} onChangeText={setPassword} secureTextEntry autoComplete="new-password" />
    <Button title="Update password" onPress={changePassword} disabled={busy || password.length < 6} />
    <Message text={message} />
    <Button title="Sign out" onPress={() => { void supabase?.auth.signOut(); }} disabled={busy} />
    <Button title="Delete account" onPress={deleteAccount} disabled={busy} danger />
  </Page>;
}
