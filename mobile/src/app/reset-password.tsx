import { useEffect, useState } from 'react';
import { useLinkingURL } from 'expo-linking';
import { Button, Field, Heading, Message, Page } from '../components/ui';
import { supabase } from '../lib/supabase';
import { passwordIssue } from '../lib/password';

export default function ResetPassword() {
  const url = useLinkingURL();
  const [email, setEmail] = useState(''); const [password, setPassword] = useState(''); const [confirmation, setConfirmation] = useState('');
  const [ready, setReady] = useState(false); const [busy, setBusy] = useState(false); const [message, setMessage] = useState('');
  const linkError = url ? (() => {
    const parsed = new URL(url);
    return new URLSearchParams(parsed.search).get('error_description') || new URLSearchParams(parsed.hash.slice(1)).get('error_description') || '';
  })() : '';
  useEffect(() => {
    if (!url || !supabase) return;
    const parsed = new URL(url);
    if (!parsed.pathname.includes('reset-password') && parsed.hostname !== 'reset-password') return;
    const query = new URLSearchParams(parsed.search);
    const fragment = new URLSearchParams(parsed.hash.slice(1));
    if (linkError) return;
    const tokenHash = query.get('token_hash');
    const accessToken = fragment.get('access_token'); const refreshToken = fragment.get('refresh_token');
    if (!tokenHash && (!accessToken || !refreshToken)) return;
    let active = true;
    const verify = tokenHash ? supabase.auth.verifyOtp({ token_hash: tokenHash, type: 'recovery' })
      : supabase.auth.setSession({ access_token: accessToken!, refresh_token: refreshToken! });
    verify.then(({ error: authError }) => {
      if (!active) return;
      if (authError) setMessage(authError.message); else { setReady(true); setMessage('Recovery link verified. Choose a new password.'); }
    }).catch(() => { if (active) setMessage('Could not verify the recovery link. Request a new one.'); });
    return () => { active = false; };
  }, [url, linkError]);
  async function send() {
    if (!supabase || !email.trim()) return;
    setBusy(true); setMessage('');
    try {
      const { error } = await supabase.auth.resetPasswordForEmail(email.trim(), { redirectTo: 'tradara://reset-password' });
      setMessage(error?.message ?? 'If this address has an account, check its email for a recovery link.');
    } catch { setMessage('Could not request a recovery email. Check your connection and try again.'); }
    finally { setBusy(false); }
  }
  async function update() {
    if (!supabase || passwordIssue(password, confirmation)) return;
    setBusy(true); setMessage('');
    try {
      const { error } = await supabase.auth.updateUser({ password });
      setMessage(error?.message ?? 'Password updated. You can return to Tradara.'); if (!error) { setPassword(''); setConfirmation(''); }
    } catch { setMessage('Password could not be updated. Check your connection and try again.'); }
    finally { setBusy(false); }
  }
  return <Page><Heading subtitle={ready ? 'Set a new password for your account.' : 'Enter your account email to receive a recovery link.'}>Password recovery</Heading>
    {ready ? <><Field label="New password" value={password} onChangeText={setPassword} secureTextEntry autoComplete="new-password" />
      <Field label="Confirm new password" value={confirmation} onChangeText={setConfirmation} secureTextEntry autoComplete="new-password" />
      <Button title="Set new password" onPress={() => { void update(); }} disabled={busy || !!passwordIssue(password, confirmation)} /></>
      : <><Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" autoComplete="email" />
        <Button title="Send recovery email" onPress={() => { void send(); }} disabled={busy || !email.trim()} /></>}
    <Message text={linkError || (ready && confirmation ? passwordIssue(password, confirmation) : '') || message} />
  </Page>;
}
