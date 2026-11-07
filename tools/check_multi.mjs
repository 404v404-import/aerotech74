// Проверка многостраничника: переполнение, ошибки, формы, меню
import { spawn } from 'node:child_process';

const origin = process.argv[2] || 'http://127.0.0.1:8712';
const paths = [
  '/multi/',
  '/multi/uslugi/',
  '/multi/uslugi/montazh/',
  '/multi/tseny/',
  '/multi/proekty/',
  '/multi/kontakty/',
  '/multi/blog/',
  '/multi/blog/kak-vybrat-ventilyaciyu-v-kvartire/',
  '/multi/o-kompanii/',
];
const widths = [360, 390, 480, 640, 768, 900, 1024, 1280, 1440, 1920];

const port = 9600 + Math.floor(Math.random() * 200);
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const proc = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${port}`, `--user-data-dir=/tmp/chrome-mp-${port}`,
  '--no-first-run', '--no-default-browser-check', 'about:blank',
], { stdio: 'ignore' });

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

async function getWs() {
  for (let i = 0; i < 100; i++) {
    try {
      const list = await (await fetch(`http://127.0.0.1:${port}/json/list`)).json();
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
const errors = [];
ws.onmessage = (e) => {
  const msg = JSON.parse(e.data);
  if (msg.id && pending.has(msg.id)) {
    const { resolve, reject } = pending.get(msg.id);
    pending.delete(msg.id);
    msg.error ? reject(new Error(JSON.stringify(msg.error))) : resolve(msg.result);
  } else if (msg.method === 'Runtime.exceptionThrown') {
    errors.push(msg.params.exceptionDetails.text + ' ' +
      (msg.params.exceptionDetails.exception?.description || ''));
  }
};
const send = (method, params = {}) => new Promise((resolve, reject) => {
  const mid = ++id;
  pending.set(mid, { resolve, reject });
  ws.send(JSON.stringify({ id: mid, method, params }));
});
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text);
  return r.result.value;
};

await send('Page.enable');
await send('Runtime.enable');

const report = { overflow: [], formSent: null, errors: [], h1: {}, linksBroken: [] };

for (const p of paths) {
  await send('Page.navigate', { url: origin + p });
  await sleep(700);
  for (const w of widths) {
    await send('Emulation.setDeviceMetricsOverride', { width: w, height: 900, deviceScaleFactor: 1, mobile: w < 820 });
    await sleep(120);
    const sw = await evaluate('document.documentElement.scrollWidth');
    if (sw > w + 1) report.overflow.push(`${p} @${w}: ${sw}`);
  }
  await send('Emulation.setDeviceMetricsOverride', { width: 1440, height: 900, deviceScaleFactor: 1, mobile: false });
  await sleep(150);
  report.h1[p] = await evaluate(`document.querySelectorAll('h1').length`);
}

// форма на странице контактов
await send('Page.navigate', { url: origin + '/multi/kontakty/' });
await sleep(900);
await evaluate(`(()=>{
  const f=document.getElementById('leadForm');
  f.querySelector('input[name=name]').value='Иван';
  const p=f.querySelector('input[name=phone]');
  p.value='+7 (351) 200-00-00'; p.dispatchEvent(new Event('input',{bubbles:true}));
  f.querySelector('button[type=submit]').click();
})()`);
await sleep(1200);
report.formSent = await evaluate(`document.getElementById('leadForm').classList.contains('is-sent')`);

// мобильное меню
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await sleep(300);
await evaluate(`document.getElementById('burger').click()`);
await sleep(350);
report.navOpen = await evaluate(`document.getElementById('nav').classList.contains('is-open')`);
await evaluate(`document.querySelector('#nav a').click()`);
await sleep(350);
report.navClosed = await evaluate(`!document.getElementById('nav').classList.contains('is-open')`);

report.errors = errors;

console.log(JSON.stringify(report, null, 2));
ws.close();
proc.kill();
process.exit(0);
