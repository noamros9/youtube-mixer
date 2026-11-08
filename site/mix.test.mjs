// Run: node --test site/mix.test.mjs
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { mix, shuffle } from './mix.js';

test('shuffle keeps every item', () => {
  assert.deepEqual(shuffle([1, 2, 3, 4]).sort(), [1, 2, 3, 4]);
});

test('mix never repeats a channel until every channel had a turn', () => {
  const videos = [
    ...Array.from({ length: 50 }, (_, i) => ({ c: 'busy', i })),
    { c: 'a' }, { c: 'b' }, { c: 'c' },
  ];
  const out = mix(videos, v => v.c);
  assert.equal(out.length, videos.length);
  assert.deepEqual(new Set(out.slice(0, 4).map(v => v.c)), new Set(['busy', 'a', 'b', 'c']));
  assert.ok(out.slice(4).every(v => v.c === 'busy'));
});
