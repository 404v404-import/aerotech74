// Interaction & console check for the mockup
import { spawn } from 'node:child_process';

const url = process.argv[2] || 'http://127.0.0.1:8712/';
const port = 9500 + Math.floor(Math.random() * 200);
const chrome = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const proc = spawn(chrome, [
  '--headless=new', '--no-sandbox', '--disable-gpu', '--hide-scrollbars',
  `--remote-debugging-port=${port}`,
  `--user-data-dir=/tmp/chrome-check-${port}`,
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
  if (r.exceptionDetails) throw new Error(r.exceptionDetails.text + ' ' + (r.exceptionDetails.exception?.description || ''));
  return r.result.value;
};

await send('Page.enable');
await send('Runtime.enable');
await send('Page.navigate', { url });
await sleep(1600);

const report = {};

report.title = await evaluate('document.title');
report.sections = await evaluate(`[...document.querySelectorAll('main section[id]')].map(s=>s.id)`);

// portfolio filter
report.cardsTotal = await evaluate(`document.querySelectorAll('.project').length`);
await evaluate(`document.querySelector('[data-filter="office"]').click()`);
await sleep(200);
report.cardsOffice = await evaluate(`document.querySelectorAll('.project:not(.is-hidden)').length`);
report.activeFilter = await evaluate(`document.querySelector('.filter.is-active').textContent`);
await evaluate(`document.querySelector('[data-filter="all"]').click()`);
await sleep(150);
report.cardsBack = await evaluate(`document.querySelectorAll('.project:not(.is-hidden)').length`);

// calculator
await evaluate(`(()=>{const a=document.getElementById('area');a.value=120;a.dispatchEvent(new Event('input'));})()`);
report.calc = await evaluate(`JSON.stringify({area:document.getElementById('areaOut').textContent,power:document.getElementById('powerOut').textContent,air:document.getElementById('airOut').textContent})`);

// lead form
await evaluate(`(()=>{
  const f=document.getElementById('leadForm');
  const n=f.querySelector('input[name=name]'), p=f.querySelector('input[name=phone]');
  n.value='Иван'; n.dispatchEvent(new Event('input',{bubbles:true}));
  p.value='+7 (351) 200-00-00'; p.dispatchEvent(new Event('input',{bubbles:true}));
  f.querySelector('button[type=submit]').click();
})()`);
await sleep(1200);
report.formSent = await evaluate(`document.getElementById('leadForm').classList.contains('is-sent')`);
report.maskValue = await evaluate(`document.querySelector('#leadForm input[name=phone]').value`);

// mobile nav
await send('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
await sleep(400);
report.burgerVisible = await evaluate(`getComputedStyle(document.getElementById('burger')).display`);
await evaluate(`document.getElementById('burger').click()`);
await sleep(350);
report.navOpen = await evaluate(`document.getElementById('nav').classList.contains('is-open')`);
report.navStyle = await evaluate(`getComputedStyle(document.getElementById('nav')).opacity`);
await evaluate(`document.querySelector('#nav a').click()`);
await sleep(400);
report.navClosed = await evaluate(`!document.getElementById('nav').classList.contains('is-open')`);

report.horizontalOverflow = await evaluate(`document.documentElement.scrollWidth > document.documentElement.clientWidth + 1`);
report.scrollWidth = await evaluate(`document.documentElement.scrollWidth`);
report.clientWidth = await evaluate(`document.documentElement.clientWidth`);
// responsive overflow sweep
await evaluate(`document.getElementById('burger').click()`);
const widths = [360, 390, 480, 640, 768, 820, 900, 1024, 1120, 1280, 1440, 1920];
const overflow = {};
for (const w of widths) {
  await send('Emulation.setDeviceMetricsOverride', { width: w, height: 900, deviceScaleFactor: 1, mobile: w < 820 });
  await sleep(250);
  overflow[w] = await evaluate(`document.documentElement.scrollWidth`);
}
report.scrollWidthByViewport = overflow;

report.errors = errors;

console.log(JSON.stringify(report, null, 2));
ws.close();
proc.kill();
process.exit(0);
