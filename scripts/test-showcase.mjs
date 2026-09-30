// Smoke test for the showcase viewer. Needs network for the model-viewer script and Draco decoder.
//   1. Every way of switching model (Assembled/Exploded buttons, stage buttons, component pages) must load the new model.
//   2. A hotspot tip must sit fully inside the viewer, on desktop and phone widths.
import { chromium } from 'playwright';
import { startServer } from './serve.mjs';

// BASE_URL=https://example.vercel.app/ runs against a deployed site instead of the local folder.
const { base, close } = process.env.BASE_URL ? { base: process.env.BASE_URL.replace(/\/?$/, '/'), close() {} } : await startServer();
const browser = await chromium.launch({ channel: 'chromium', args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
const failures = [];
const check = (ok, msg) => { console.log(ok ? 'ok  ' : 'FAIL', msg); if (!ok) failures.push(msg); };
const ASSEMBLED = 'gspe_pdu_apdu9953.glb', EXPLODED = 'gspe_pdu_apdu9953_exploded.glb';

async function open(viewport, path, viewerSel, label) {
  const page = await browser.newPage({ viewport });
  page.errors = []; page.requests = [];
  page.on('request', r => page.requests.push(r.url()));
  page.on('pageerror', e => page.errors.push(e.message));
  page.on('console', m => { if (m.type() === 'error' && !m.location().url.includes('favicon')) page.errors.push(`${m.text()} (${m.location().url})`); });
  await page.goto(base + path);
  await page.waitForTimeout(1500);
  check(!page.requests.some(u => /model-viewer|\.glb/.test(u)), `${label}: no viewer library or model before the first click`);
  await page.evaluate(s => { const v = document.querySelector(s); window.__loads = 0; v.addEventListener('load', () => window.__loads++); }, viewerSel);
  return page;
}


// Everything must come from our own origin (CSP would also block it), and the Plex font must be ours.
async function checkSelfContained(page, label) {
  const external = page.requests.filter(u => !u.startsWith(base) && !/^(data|blob):/.test(u));
  check(external.length === 0, `${label}: nothing loaded from other origins${external.length ? ' -> ' + external[0] : ''}`);
  const weights = await page.evaluate(async () => { await document.fonts.ready; return [...document.fonts].filter(f => f.family.includes('IBM Plex Sans') && f.status === 'loaded').length; });
  check(weights >= 2, `${label}: self-hosted Plex font loaded (${weights} weights)`);
}

// Runs `action`, then requires a new `load` event and the expected src.
async function expectLoad(page, viewerSel, label, action, file) {
  const before = await page.evaluate(() => window.__loads);
  await action();
  let ok = true;
  try { await page.waitForFunction(n => window.__loads > n, before, { timeout: 40000 }); } catch { ok = false; }
  const src = await page.evaluate(s => document.querySelector(s).getAttribute('src'), viewerSel);
  check(ok && src.endsWith(file), `${label} -> ${file}`);
}

for (const [name, viewport] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
  const sel = '#interactive-inspection', vsel = `${sel} model-viewer`;
  const page = await open(viewport, 'index.html', vsel, name);
  await page.locator(`${sel} [data-load-3d]`).scrollIntoViewIfNeeded();
  await expectLoad(page, vsel, `${name}: load button`, () => page.locator(`${sel} [data-load-3d]`).click(), ASSEMBLED);
  for (const [mode, file] of [['exploded', EXPLODED], ['assembled', ASSEMBLED], ['exploded', EXPLODED]]) {
    await expectLoad(page, vsel, `${name}: ${mode} button`, () => page.locator(`${sel} [data-mode="${mode}"]`).click(), file);
  }
  if (name === 'desktop') {
    for (const [stage, file] of [[6, ASSEMBLED], [7, EXPLODED], [4, EXPLODED], [5, ASSEMBLED]]) {
      const prev = await page.evaluate(s => document.querySelector(s).getAttribute('src'), vsel);
      if (prev.endsWith(file)) { // same model as before, so no new load is expected
        await page.locator(`${sel} [data-stage="${stage}"]`).click();
        check(true, `${name}: stage ${stage} keeps ${file}`);
      } else {
        await expectLoad(page, vsel, `${name}: stage ${stage}`, () => page.locator(`${sel} [data-stage="${stage}"]`).click(), file);
      }
    }
  }
  await page.locator(`${sel} [data-mode="assembled"]`).click();
  await page.waitForFunction(() => window.__loads > 0);
  await page.waitForTimeout(2500);
  for (const slot of ['hotspot-nmc', 'hotspot-outlets']) {
    await page.evaluate(([s, slot]) => document.querySelector(`${s} .hotspot[slot="${slot}"]`).click(), [sel, slot]);
    await page.waitForTimeout(1800); // camera easing
    const box = await page.evaluate(([s, slot]) => {
      const v = document.querySelector(s + ' model-viewer').getBoundingClientRect();
      const c = document.querySelector(`${s} .hotspot[slot="${slot}"] .hotspot-card`).getBoundingClientRect();
      return { v, c, shown: c.width > 0 };
    }, [sel, slot]);
    const inside = box.shown && box.c.left >= box.v.left - 1 && box.c.right <= box.v.right + 1 && box.c.top >= box.v.top - 1 && box.c.bottom <= box.v.bottom + 1;
    check(inside, `${name}: ${slot} tip inside viewer (card ${Math.round(box.c.left)},${Math.round(box.c.top)} ${Math.round(box.c.width)}x${Math.round(box.c.height)} in viewer ${Math.round(box.v.left)},${Math.round(box.v.top)} ${Math.round(box.v.width)}x${Math.round(box.v.height)})`);
  }
  await checkSelfContained(page, name);
  check(page.errors.length === 0, `${name}: no console errors${page.errors.length ? ' -> ' + page.errors[0] : ''}`);
  await page.close();
}

// Component pages: nmc3 starts on the assembled model, internal-busbars-pcb starts on the exploded one.
for (const [file, first, others] of [['nmc3', ASSEMBLED, [['exploded', EXPLODED], ['assembled', ASSEMBLED]]], ['internal-busbars-pcb', EXPLODED, [['assembled', ASSEMBLED], ['exploded', EXPLODED]]]]) {
  const vsel = 'model-viewer[data-component-viewer]';
  const page = await open({ width: 1440, height: 900 }, `components/${file}.html`, vsel, file);
  await expectLoad(page, vsel, `${file}: load button`, () => page.locator('[data-load-3d]').click(), first);
  for (const [mode, f] of others) await expectLoad(page, vsel, `${file}: ${mode} button`, () => page.locator(`[data-mode="${mode}"]`).click(), f);
  if (file === 'nmc3') { // ARIA tabs: arrow key moves selection and shows the matching panel
    await page.locator('#tab-rj45').focus();
    await page.keyboard.press('ArrowRight');
    const tabs = await page.evaluate(() => ({ selected: document.querySelector('#tab-usb-a').getAttribute('aria-selected'), panelHidden: document.querySelector('#panel-usb-a').hidden, oldHidden: document.querySelector('#panel-rj45').hidden, focused: document.activeElement.id }));
    check(tabs.selected === 'true' && !tabs.panelHidden && tabs.oldHidden && tabs.focused === 'tab-usb-a', `${file}: arrow key selects next tab`);
  }
  await checkSelfContained(page, file);
  check(page.errors.length === 0, `${file}: no console errors${page.errors.length ? ' -> ' + page.errors[0] : ''}`);
  await page.close();
}

await browser.close();
close();
console.log(failures.length ? `\n${failures.length} FAILED` : '\nall passed');
process.exit(failures.length ? 1 : 0);
