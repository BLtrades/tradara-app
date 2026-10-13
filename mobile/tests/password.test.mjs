import { test } from 'node:test';
import assert from 'node:assert/strict';
import { MIN_PASSWORD_LENGTH, PASSWORD_REQUIREMENTS, passwordIssue } from '../src/lib/password.ts';

test('rejects a password below the configured minimum', () => {
  assert.equal(MIN_PASSWORD_LENGTH, 8);
  assert.match(passwordIssue('Sh0rt!', 'Sh0rt!'), /at least 8/);
});

test('requires a mixed password for new and changed accounts', () => {
  assert.match(PASSWORD_REQUIREMENTS, /uppercase.*lowercase.*number.*special/i);
  assert.match(passwordIssue('PASSWORD1!', 'PASSWORD1!'), /lowercase/);
  assert.match(passwordIssue('password1!', 'password1!'), /uppercase/);
  assert.match(passwordIssue('Password!', 'Password!'), /number/);
  assert.match(passwordIssue('Password1', 'Password1'), /special/);
});

test('rejects a mistyped password confirmation', () => {
  assert.match(passwordIssue('Secure-pass1', 'Secure-pass2'), /do not match/);
});

test('accepts matching passwords that meet the minimum', () => {
  assert.equal(passwordIssue('Secure-pass1!', 'Secure-pass1!'), '');
});
