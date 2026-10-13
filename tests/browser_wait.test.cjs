const test = require('node:test');
const assert = require('node:assert/strict');
const {waitForPageCondition} = require('../scripts/browser_wait.cjs');

test('passes the argument and accepts an immediately true condition', async () => {
  const page = {evaluate: async (predicate, argument) => predicate(argument)};
  await waitForPageCondition(page, value => value === 'ready', 'ready', {timeout: 0});
});

test('rechecks from the host when the first evaluation is false', async () => {
  let calls = 0;
  const page = {evaluate: async () => ++calls === 3};
  await waitForPageCondition(page, () => true, undefined, {timeout: 1000, interval: 1});
  assert.equal(calls, 3);
});

test('times out when the condition remains false', async () => {
  const page = {evaluate: async () => false};
  await assert.rejects(waitForPageCondition(page, () => false, undefined, {timeout: 0}),
    /Page condition timed out after 0ms/);
});

test('the deadline also bounds an evaluation that never settles', async () => {
  const page = {evaluate: () => new Promise(() => {})};
  await assert.rejects(waitForPageCondition(page, () => false, undefined, {timeout: 0}),
    /Page condition timed out after 0ms/);
});

test('preserves the original browser evaluation error', async () => {
  const failure = new Error('Browser disconnected');
  const page = {evaluate: async () => { throw failure; }};
  await assert.rejects(waitForPageCondition(page, () => true), error => error === failure);
});

test('rejects invalid timeout and polling interval options', async () => {
  const page = {evaluate: async () => true};
  for (const options of [{timeout: -1}, {timeout: Infinity}, {interval: 0}, {interval: NaN}]) {
    await assert.rejects(waitForPageCondition(page, () => true, undefined, options), RangeError);
  }
});
