// CDP screenshot helper for the mockup
// usage: node tools/shot.mjs <url> <out.png> <width> <height> [full|viewport] [mobile]
import { spawn } from 'node:child_process';
import { writeFileSync, mkdirSync } from 'node:fs';
import { dirname } from 'node:path';

const [url, out, w = '1440', h = '900', mode = 'full', mobileFlag = '', pre = ''] = process.argv.slice(2);
const width = Number(w), height = Number(h);
const mobile = mobileFlag === 'mobile';
const port = 9333 + Math.floor(Math.random() * 200);
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const proc = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  '--force-prefers-reduced-motion',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=/tmp/chrome-cdp-${port}`,
  '--no-first-run', '--no-default-browser-check',
  'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWs() {
  for (let i = 0; i < 100; i++) {
    try {
      const res = await fetch(`http://127.0.0.1:${port}/json/list`);
      const list = await res.json();
      const page = list.find((t) => t.type === 'page');
      if (page) return page.webSocketDebuggerUrl;
    } catch {}
    await sleep(150);
  }
  throw new Error('CDP not ready');
}

const ws = new WebSocket(await getWs());
await new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });

let id = 0;
const pending = new Map();
const events = new Map();

ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
  } else if (msg.method) {
    const arr = events.get(msg.method) || [];
    arr.forEach((fn) => fn(msg.params));
    events.delete(msg.method);
  }
};

const send = (method, params = {}) => new Promise((resolve, reject) => {
  const mid = ++id;
  pending.set(mid, { resolve, reject });
  ws.send(JSON.stringify({ id: mid, method, params }));
});

const once = (method) => new Promise((resolve) => {
  const arr = events.get(method) || [];
  arr.push(resolve);
  events.set(method, arr);
});

await send('Page.enable');
await send('Runtime.enable');
await send('Emulation.setDeviceMetricsOverride', {
  width, height, deviceScaleFactor: mobile ? 2 : 1, mobile,
});
await send('Emulation.setEmulatedMedia', { features: [{ name: 'prefers-reduced-motion', value: 'reduce' }] });

const loaded = once('Page.loadEventFired');
await send('Page.navigate', { url });
await loaded;
await sleep(900);

// trigger lazy reveal animations, then come back to the top
await send('Runtime.evaluate', {
  expression: `window.scrollTo(0, document.body.scrollHeight);`,
});
await sleep(800);
await send('Runtime.evaluate', { expression: `window.scrollTo(0, 0);` });
await sleep(500);
await send('Runtime.evaluate', { expression: `document.fonts && document.fonts.ready` });
if (pre) {
  await send('Runtime.evaluate', { expression: pre, awaitPromise: true });
  await sleep(1500);
}

// freeze the counters at their final values for a deterministic screenshot
await send('Runtime.evaluate', {
  expression: `document.querySelectorAll('[data-count]').forEach(function(el){el.textContent=(+el.getAttribute('data-count')).toLocaleString('ru-RU');});`,
});
await sleep(400);

const metrics = await send('Runtime.evaluate', {
  expression: `JSON.stringify({h: Math.max(document.body.scrollHeight, document.documentElement.scrollHeight), w: document.documentElement.clientWidth})`,
  returnByValue: true,
});
const { h: docH } = JSON.parse(metrics.result.value);
const shotH = mode === 'full' ? docH : height;

mkdirSync(dirname(out), { recursive: true });

if (shotH > 15000) {
  // split tall pages into chunks
  let y = 0, part = 0;
  while (y < shotH) {
    const chunk = Math.min(7000, shotH - y);
    const { data } = await send('Page.captureScreenshot', {
      format: 'png', captureBeyondViewport: true,
      clip: { x: 0, y, width, height: chunk, scale: 1 },
    });
    writeFileSync(out.replace(/\.png$/, `-${part}.png`), Buffer.from(data, 'base64'));
    y += chunk; part++;
  }
  console.log(JSON.stringify({ out, parts: part, docH, width }));
} else {
  const { data } = await send('Page.captureScreenshot', {
    format: 'png', captureBeyondViewport: true,
    clip: { x: 0, y: 0, width, height: shotH, scale: 1 },
  });
  writeFileSync(out, Buffer.from(data, 'base64'));
  console.log(JSON.stringify({ out, docH, width, height: shotH }));
}

ws.close();
proc.kill();
process.exit(0);
