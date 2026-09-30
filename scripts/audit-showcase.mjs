// Pre-deploy audit of showcase/: links, head metadata, accessibility (axe), overflow, first-load weight.
// Needs network for the model-viewer script and the axe-core script.
import { chromium } from 'playwright';
import { startServer } from './serve.mjs';

const pages = ['index.html', 'components/index.html', ...['housing', 'mounting', 'power', 'breakers', 'outlet-banks', 'nmc3', 'internal-busbars-pcb'].map(n => `components/${n}.html`)];
const { base, close } = await startServer();
const browser = await chromium.launch({ channel: 'chromium', args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
const kb = n => `${(n / 1024).toFixed(0)} KB`;
const axeRules = new Map(), problems = [];

for (const [device, viewport] of [['desktop', { width: 1440, height: 900 }], ['phone', { width: 390, height: 844 }]]) {
  for (const path of pages) {
    const page = await browser.newPage({ viewport });
    const bytes = new Map(), logs = [];
    page.on('response', async r => { try { bytes.set(r.url(), (await r.body()).length); } catch {} });
    page.on('console', m => { if (['error', 'warning'].includes(m.type()) && !m.location().url.includes('favicon')) logs.push(`${m.type()}: ${m.text().slice(0, 100)}`); });
    await page.goto(base + path);
    await page.waitForTimeout(2500);
    const info = await page.evaluate(() => ({
      description: !!document.querySelector('meta[name=description]'),
      og: !!document.querySelector('meta[property="og:image"]'),
      icon: !!document.querySelector('link[rel~=icon]'),
      h1: document.querySelectorAll('h1').length,
      noAlt: [...document.querySelectorAll('img:not([alt])')].length,
      overflowX: document.documentElement.scrollWidth - innerWidth,
      links: [...document.querySelectorAll('a[href]')].map(a => a.getAttribute('href')).filter(h => !/^(https?:|mailto:)/.test(h)),
    }));
    const broken = [];
    for (const href of new Set(info.links)) {
      const url = new URL(href, page.url());
      if (url.hash && url.pathname === new URL(page.url()).pathname && !(await page.evaluate(id => !!document.getElementById(id), url.hash.slice(1)))) broken.push(href);
      else if (!href.startsWith('#') && (await page.request.get(url.href.split('#')[0])).status() !== 200) broken.push(href);
    }
    const total = [...bytes.values()].reduce((a, b) => a + b, 0); // measured before axe is injected
    const biggest = [...bytes].sort((a, b) => b[1] - a[1])[0];
    await page.addScriptTag({ url: 'https://cdn.jsdelivr.net/npm/axe-core@4.10.2/axe.min.js' });
    const axe = await page.evaluate(() => axe.run(document, { runOnly: ['wcag2a', 'wcag2aa', 'wcag21aa', 'wcag22aa', 'best-practice'] }));
    for (const v of axe.violations) {
      const k = `${v.id} [${v.impact}]`;
      const e = axeRules.get(k) || { help: v.help, where: new Set(), nodes: 0, sample: v.nodes[0]?.target.join(' ') };
      e.where.add(`${device}:${path}`); e.nodes += v.nodes.length; axeRules.set(k, e);
    }
    console.log(`${device.padEnd(7)} ${path.padEnd(38)} ${String(bytes.size).padStart(2)} req ${kb(total).padStart(7)} | biggest ${biggest[0].split('/').pop().slice(0, 28)} ${kb(biggest[1])}${info.overflowX > 0 ? ` | OVERFLOW-X +${info.overflowX}px` : ''}${broken.length ? ` | BROKEN LINKS ${broken}` : ''}${logs.length ? ` | ${logs.length} console: ${logs[0]}` : ''}`);
    if (device === 'desktop') problems.push([path, info]);
    await page.close();
  }
}
console.log('\n== head metadata (per page) ==');
for (const [p, i] of problems) console.log(p.padEnd(38), `description:${i.description} og:image:${i.og} favicon:${i.icon} h1:${i.h1} img-without-alt:${i.noAlt}`);
console.log('\n== axe violations ==');
if (!axeRules.size) console.log('none');
for (const [k, e] of axeRules) console.log(`${k}: ${e.help} | ${e.nodes} nodes on ${e.where.size} page-views | e.g. ${e.sample}`);
await browser.close();
close();
