import { useState } from 'react';
import { Text } from 'react-native';
import { router } from 'expo-router';
import { Button, Field, Heading, Message, Page, colors } from '../components/ui';
import { configured, supabase } from '../lib/supabase';

export default function SignIn() {
  const [email, setEmail] = useState(''); const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false); const [message, setMessage] = useState('');
  async function submit(create: boolean) {
    if (!supabase) return;
    setBusy(true); setMessage('');
    try {
      const { error, data } = create ? await supabase.auth.signUp({ email: email.trim(), password }) : await supabase.auth.signInWithPassword({ email: email.trim(), password });
      setMessage(error?.message ?? (create && !data.session ? 'Check your email to confirm your account.' : ''));
    } catch { setMessage('Could not reach the account service. Try again.'); }
    finally { setBusy(false); }
  }
  return <Page><Heading subtitle="Your construction opportunities and pipeline in one place.">Tradara</Heading>
    {!configured ? <Text style={{ color: colors.danger }}>Set EXPO_PUBLIC_SUPABASE_URL and EXPO_PUBLIC_SUPABASE_PUBLISHABLE_KEY to connect this build.</Text> : null}
    <Field label="Email" value={email} onChangeText={setEmail} keyboardType="email-address" autoCapitalize="none" autoComplete="email" />
    <Field label="Password" value={password} onChangeText={setPassword} secureTextEntry autoComplete="password" />
    <Message text={message} />
    <Button title="Sign in" disabled={busy || !configured || !email || !password} onPress={() => submit(false)} />
    <Button title="Create account" disabled={busy || !configured || !email || password.length < 6} onPress={() => submit(true)} />
    <Button title="Forgot password?" onPress={() => router.push('/reset-password')} />
  </Page>;
}
