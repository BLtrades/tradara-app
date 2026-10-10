import { useState } from 'react';
import { Alert, Text } from 'react-native';
import { Button, Field, Heading, Message, Page, styles } from '../../components/ui';
import { supabase } from '../../lib/supabase';
import { useSession } from '../../lib/session';
import { passwordIssue } from '../../lib/password';

export default function Settings() {
  const { session } = useSession(); const [password, setPassword] = useState(''); const [confirmation, setConfirmation] = useState(''); const [message, setMessage] = useState(''); const [busy, setBusy] = useState(false);
  async function changePassword() {
    if (!supabase || passwordIssue(password, confirmation)) return;
    setBusy(true); setMessage('');
    try {
      const { error } = await supabase.auth.updateUser({ password });
      setMessage(error?.message ?? 'Password updated.'); if (!error) { setPassword(''); setConfirmation(''); }
    } catch { setMessage('Password could not be updated. Check your connection and try again.'); }
    finally { setBusy(false); }
  }
  async function signOut() {
    if (!supabase) return;
    setBusy(true); setMessage('');
    try {
      const { error } = await supabase.auth.signOut({ scope: 'local' });
      if (error) setMessage(error.message);
    } catch { setMessage('Could not sign out on this device. Check your connection and try again.'); }
    finally { setBusy(false); }
  }
  function deleteAccount() { Alert.alert('Delete account permanently?', 'Your profile and pipeline will be removed. This cannot be undone.', [
    { text: 'Cancel', style: 'cancel' }, { text: 'Delete account', style: 'destructive', onPress: async () => {
      if (!supabase) return;
      setBusy(true); setMessage('');
      try {
        const { error } = await supabase.rpc('delete_my_account');
        if (error) { setMessage(error.message); return; }
        await supabase.auth.signOut({ scope: 'local' });
      } catch { setMessage('Account deletion failed. Your account remains active. Please try again.'); }
      finally { setBusy(false); }
    } },
  ]); }
  return <Page><Heading subtitle="Manage your account and privacy.">Settings</Heading>
    <Text style={styles.muted}>Signed in as {session?.user.email}</Text>
    <Field label="New password" value={password} onChangeText={setPassword} secureTextEntry autoComplete="new-password" />
    <Field label="Confirm new password" value={confirmation} onChangeText={setConfirmation} secureTextEntry autoComplete="new-password" />
    <Button title="Update password" onPress={changePassword} disabled={busy || !!passwordIssue(password, confirmation)} />
    <Message text={(confirmation ? passwordIssue(password, confirmation) : '') || message} />
    <Button title="Sign out" onPress={() => { void signOut(); }} disabled={busy} />
    <Button title="Delete account" onPress={deleteAccount} disabled={busy} danger />
  </Page>;
}
