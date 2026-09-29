import { test } from 'node:test';
import assert from 'node:assert/strict';
import { deleteTradaraAccount } from './delete-account.mjs';

test('requires explicit confirmation before contacting Supabase', async () => {
  let called = false;
  await assert.rejects(deleteTradaraAccount('a@example.com', 'password', 'delete', () => { called = true; }), /DELETE/);
  assert.equal(called, false);
});

test('authenticates then deletes only with the returned bearer token', async () => {
  const calls = [];
  const fakeFetch = async (url, options) => {
    calls.push({ url, options });
    return calls.length === 1 ? { ok: true, json: async () => ({ access_token: 'signed-in-user-token' }) } : { ok: true };
  };
  await deleteTradaraAccount(' a@example.com ', 'password', 'DELETE', fakeFetch);
  assert.equal(calls.length, 2);
  assert.match(calls[0].url, /\/auth\/v1\/token\?grant_type=password$/);
  assert.deepEqual(JSON.parse(calls[0].options.body), { email: 'a@example.com', password: 'password' });
  assert.match(calls[1].url, /\/rest\/v1\/rpc\/delete_my_account$/);
  assert.equal(calls[1].options.headers.Authorization, 'Bearer signed-in-user-token');
});

test('does not attempt deletion when sign-in fails', async () => {
  let calls = 0;
  await assert.rejects(deleteTradaraAccount('a@example.com', 'wrong', 'DELETE', async () => { calls++; return { ok: false }; }), /Sign-in failed/);
  assert.equal(calls, 1);
});
