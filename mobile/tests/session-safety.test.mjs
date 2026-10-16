import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const settings = await readFile(new URL('../src/app/(tabs)/settings.tsx', import.meta.url), 'utf8');

test('normal and post-deletion sign-out only clear the current device session', () => {
  const localSignOuts = settings.match(/auth\.signOut\(\{ scope: 'local' \}\)/g) || [];
  assert.equal(localSignOuts.length, 2);
  assert.doesNotMatch(settings, /auth\.signOut\(\)/);
});

test('account actions always release the busy state', () => {
  assert.match(settings, /finally \{ setBusy\(false\); \}/);
  assert.equal((settings.match(/finally \{ setBusy\(false\); \}/g) || []).length, 3);
});
