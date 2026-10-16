import { test } from 'node:test';
import assert from 'node:assert/strict';
import { fetchOpportunities, RADAR_REQUEST_TIMEOUT_MS, scoreFeatures } from '../src/lib/radar.ts';

const now = new Date('2026-09-29T00:00:00Z');
const feature = (description, months, decision = 'Approved') => ({ attributes: {
  description, decision, developmentnumber: 'DEV-1', decisiondate: months === null ? null : now.getTime() - Math.round(months * 30.44 * 86400000),
  applicationurl: 'https://example.test/project',
} });

test('matches the web score and trade window for an approved electrical project', () => {
  const [row] = scoreFeatures({ features: [feature('New commercial building', 5)] }, ['Electrician'], null, now);
  assert.equal(row.score, 84);
  assert.equal(row.action, 'CONTACT NOW — trade window');
  assert.equal(row.development, 'DEV-1');
});

test('company preferences boost a matching opportunity without exceeding 100', () => {
  const [row] = scoreFeatures({ features: [feature('New commercial building', 5)] }, ['Electrician'],
    { preferred_trades: ['Electrician'], preferred_project_types: ['commercial'] }, now);
  assert.equal(row.score, 100);
  assert.equal(row.why, 'preferred project type, core company trade, good timing');
});

test('handles malformed data and missing dates', () => {
  assert.deepEqual(scoreFeatures({ features: [null, 'bad', { attributes: null }] }, ['Electrician'], null, now), []);
  assert.equal(scoreFeatures({ features: [feature('Apartment building', null)] }, ['HVAC'], null, now)[0].action, 'VERIFY TIMING');
});

test('Radar requests use a launch-safe timeout and explain timeouts', async () => {
  assert.equal(RADAR_REQUEST_TIMEOUT_MS, 15000);
  const neverResponds = (_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
  });
  await assert.rejects(fetchOpportunities(undefined, 5, neverResponds), /request timed out.*try again/i);
});

test('Radar requests preserve caller cancellation without reporting a timeout', async () => {
  const controller = new AbortController();
  const neverResponds = (_url, { signal }) => new Promise((_resolve, reject) => {
    signal.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')), { once: true });
  });
  const request = fetchOpportunities(controller.signal, 1000, neverResponds);
  controller.abort();
  await assert.rejects(request, error => error.name === 'AbortError');
});
