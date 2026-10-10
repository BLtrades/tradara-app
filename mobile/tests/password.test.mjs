import { test } from 'node:test';
import assert from 'node:assert/strict';
import { MIN_PASSWORD_LENGTH, passwordIssue } from '../src/lib/password.ts';

test('rejects a password below the configured minimum', () => {
  assert.equal(MIN_PASSWORD_LENGTH, 6);
  assert.match(passwordIssue('short', 'short'), /at least 6/);
});

test('rejects a mistyped password confirmation', () => {
  assert.match(passwordIssue('secure-password', 'secure-passw0rd'), /do not match/);
});

test('accepts matching passwords that meet the minimum', () => {
  assert.equal(passwordIssue('secure-password', 'secure-password'), '');
});
