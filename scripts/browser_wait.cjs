// Playwright's in-page polling timers can stop when page JavaScript is disabled.
// Poll from Node instead; preserve evaluation errors and bound the entire wait.
const {setTimeout: delay} = require('node:timers/promises');

async function waitForPageCondition(page, predicate, argument, options = {}) {
  const {timeout = 30000, interval = 100} = options;
  if (!Number.isFinite(timeout) || timeout < 0 || !Number.isFinite(interval) || interval <= 0) {
    throw new RangeError('Wait timeout must be nonnegative and interval must be positive');
  }
  const controller = new AbortController();
  let deadline;
  const expired = new Promise((_, reject) => {
    deadline = setTimeout(() => reject(new Error(`Page condition timed out after ${timeout}ms`)), timeout);
  });
  const poll = async () => {
    while (!controller.signal.aborted) {
      if (await page.evaluate(predicate, argument)) return;
      await delay(interval, undefined, {signal: controller.signal});
    }
  };
  try {
    await Promise.race([poll(), expired]);
  } finally {
    clearTimeout(deadline);
    controller.abort();
  }
}

module.exports = {waitForPageCondition};
