const SUPABASE_URL = 'https://lxrjawzqfqrnswrjxovk.supabase.co';
const PUBLISHABLE_KEY = 'sb_publishable_ddJGlAsCJ86PVJQmKYxvLA_6FrjoB9b';

/** Delete only the account authenticated by these credentials. No token is stored. */
export async function deleteTradaraAccount(email, password, confirmation, fetcher = fetch) {
  if (confirmation !== 'DELETE') throw new Error('Type DELETE to confirm.');
  if (!email.trim() || !password) throw new Error('Enter your Tradara email and password.');

  const auth = await fetcher(`${SUPABASE_URL}/auth/v1/token?grant_type=password`, {
    method: 'POST',
    headers: { apikey: PUBLISHABLE_KEY, 'Content-Type': 'application/json' },
    body: JSON.stringify({ email: email.trim(), password }),
  });
  if (!auth.ok) throw new Error('Sign-in failed. Check your email and password.');
  const session = await auth.json();
  if (typeof session.access_token !== 'string' || !session.access_token) throw new Error('Could not verify your account.');

  const deletion = await fetcher(`${SUPABASE_URL}/rest/v1/rpc/delete_my_account`, {
    method: 'POST',
    headers: { apikey: PUBLISHABLE_KEY, Authorization: `Bearer ${session.access_token}`, 'Content-Type': 'application/json' },
    body: '{}',
  });
  if (!deletion.ok) throw new Error('Account deletion could not be completed. Your account remains active. Please try again later.');
}
