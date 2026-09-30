// Renders the poster shown before a visitor loads the 3D model: one JPEG per model-viewer in showcase/.
// Run after `npm run build:web` so each poster matches the model and camera the page starts with.
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';
import { join } from 'node:path';
import { root, startServer } from './serve.mjs';

const out = join(root, 'assets/posters');
const { base, close } = await startServer();

const targets = [
  ['index.html', '.hero-art model-viewer', 'home-hero'],
  ['index.html', '#interactive-inspection model-viewer', 'home-inspection'],
  ...['housing', 'mounting', 'power', 'breakers', 'outlet-banks', 'nmc3', 'internal-busbars-pcb']
    .map(n => [`components/${n}.html`, 'model-viewer[data-component-viewer]', n]),
];

await mkdir(out, { recursive: true });
const browser = await chromium.launch({ channel: 'chromium', args: ['--enable-unsafe-swiftshader', '--use-angle=swiftshader'] });
for (const [file, selector, name] of targets) {
  const page = await browser.newPage({ viewport: { width: 1440, height: 900 } });
  await page.goto(base + file);
  await page.addStyleTag({ content: '.hotspot,.viewer-tools,.viewer-label,.load-3d{visibility:hidden!important}' });
  const viewer = page.locator(selector);
  await viewer.evaluate(v => new Promise(done => {
    v.setAttribute('interaction-prompt', 'none'); // keep the hand icon out of the poster
    v.addEventListener('load', done, { once: true });
    v.querySelector('[data-load-3d]').click();
  }));
  await page.waitForTimeout(3000); // camera easing and first frames
  await viewer.screenshot({ path: join(out, `${name}.jpg`), type: 'jpeg', quality: 82 });
  console.log('poster', name);
  await page.close();
}
await browser.close();
close();
