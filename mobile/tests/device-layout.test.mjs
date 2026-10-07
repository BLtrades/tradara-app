import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const ui = await readFile(new URL('../src/components/ui.tsx', import.meta.url), 'utf8');
const layout = await readFile(new URL('../src/app/_layout.tsx', import.meta.url), 'utf8');
const signIn = await readFile(new URL('../src/app/sign-in.tsx', import.meta.url), 'utf8');

test('root layout provides safe-area context on native and web', () => {
  assert.match(layout, /<SafeAreaProvider>/);
  assert.match(layout, /<\/SafeAreaProvider>/);
});

test('pages protect gesture edges and headerless screens protect the top edge', () => {
  assert.match(ui, /\['right', 'bottom', 'left'\]/);
  assert.match(ui, /\['top', 'right', 'bottom', 'left'\]/);
  assert.match(signIn, /<Page safeTop>/);
  assert.match(layout, /<Page safeTop>/);
});

test('forms remain usable with native keyboards and shared controls expose state', () => {
  assert.match(ui, /<KeyboardAvoidingView/);
  assert.match(ui, /Platform\.OS === 'ios' \? 'padding' : 'height'/);
  assert.match(ui, /keyboardDismissMode=/);
  assert.match(ui, /accessibilityLabel=\{props\.accessibilityLabel \|\| label\}/);
  assert.match(ui, /accessibilityState=\{\{ disabled: !!disabled \}\}/);
  assert.match(ui, /accessibilityRole="progressbar"/);
});
