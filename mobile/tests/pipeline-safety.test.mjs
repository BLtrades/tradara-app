import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const pipeline = await readFile(new URL('../src/app/(tabs)/pipeline.tsx', import.meta.url), 'utf8');

test('pipeline updates report success only after Supabase accepts the write', () => {
  assert.match(pipeline, /async function update\(.*?\): Promise<boolean>/s);
  assert.match(pipeline, /if \(error\) \{ setMessage\(error\.message\); return false; \}/);
  assert.match(pipeline, /await refresh\(\); return true;/);
  assert.match(pipeline, /catch \{.*?return false; \}/s);
});

test('failed detail and status writes preserve the open editor', () => {
  assert.match(pipeline, /if \(await update\(row, \{ notes, est_value: amount \}\)\) setEditing\(null\)/);
  assert.match(pipeline, /if \(await update\(row, \{ status \}\)\) setChoosing\(null\)/);
  assert.doesNotMatch(pipeline, /void update\(row, \{ status \}\); setChoosing\(null\)/);
});
