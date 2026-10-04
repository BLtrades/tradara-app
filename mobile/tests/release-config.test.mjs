import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';

const readJson = async (path) => JSON.parse(await readFile(new URL(path, import.meta.url), 'utf8'));
const readPngHeader = async (path) => {
  const png = await readFile(new URL(path, import.meta.url));
  assert.equal(png.subarray(1, 4).toString(), 'PNG');
  return { width: png.readUInt32BE(16), height: png.readUInt32BE(20), colorType: png[25] };
};

test('Expo config contains the release identity and native assets', async () => {
  const { expo } = await readJson('../app.json');

  assert.equal(expo.name, 'Tradara');
  assert.equal(expo.slug, 'tradara');
  assert.equal(expo.scheme, 'tradara');
  assert.match(expo.version, /^\d+\.\d+\.\d+$/);
  assert.equal(expo.icon, './assets/icon.png');
  assert.equal(expo.ios.icon, './assets/icon-ios.png');
  assert.equal(expo.android.adaptiveIcon.foregroundImage, './assets/icon.png');
  assert.equal(expo.web.favicon, './assets/favicon.png');
});

test('iOS icon is an opaque 1024px square and splash artwork is high resolution', async () => {
  const icon = await readPngHeader('../assets/icon-ios.png');
  const splash = await readPngHeader('../assets/splash-icon.png');

  assert.deepEqual(icon, { width: 1024, height: 1024, colorType: 2 });
  assert.equal(splash.width, 1024);
  assert.equal(splash.height, 1024);
});

test('EAS config separates installable previews from store builds', async () => {
  const eas = await readJson('../eas.json');

  assert.equal(eas.build.preview.distribution, 'internal');
  assert.equal(eas.build.preview.android.buildType, 'apk');
  assert.equal(eas.build.production.autoIncrement, true);
  assert.deepEqual(eas.submit.production, {});
});

test('production identifiers remain an explicit owner gate', async () => {
  const { expo } = await readJson('../app.json');

  assert.equal(expo.ios.bundleIdentifier, undefined);
  assert.equal(expo.android.package, undefined);
});
