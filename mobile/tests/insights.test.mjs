import { test } from 'node:test';
import assert from 'node:assert/strict';
import { buildInsights } from '../src/lib/insights.ts';

test('summarises capacity using won and quoted values', () => {
  const insight = buildInsights([
    { status: 'Won', trade: 'Electrician', est_value: 20000 },
    { status: 'Quoted', trade: 'Electrician', est_value: 12000 },
    { status: 'Contacted', trade: 'Plumber', est_value: 5000 },
  ], 50000);
  assert.deepEqual({ won: insight.won, quoted: insight.quoted, active: insight.active, unfilled: insight.unfilled },
    { won: 20000, quoted: 12000, active: 2, unfilled: 30000 });
});

test('calculates completed-opportunity win rates by trade', () => {
  const insight = buildInsights([
    { status: 'Won', trade: 'Electrician', est_value: 1 },
    { status: 'Lost', trade: 'Electrician', est_value: 1 },
    { status: 'Won', trade: 'Plumber', est_value: 1 },
  ], 0);
  assert.deepEqual(insight.performance, [
    { trade: 'Electrician', decisions: 2, wins: 1, winRate: 0.5 },
    { trade: 'Plumber', decisions: 1, wins: 1, winRate: 1 },
  ]);
});

test('ignores invalid money values and never reports a negative gap', () => {
  const insight = buildInsights([
    { status: 'Won', trade: 'Electrician', est_value: 'bad' },
    { status: 'Won', trade: 'Electrician', est_value: -20 },
    { status: 'Won', trade: 'Electrician', est_value: 200 },
  ], 100);
  assert.equal(insight.won, 200);
  assert.equal(insight.unfilled, 0);
});
