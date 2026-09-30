// Minimal static server for showcase/, used by the poster, test and audit scripts.
// It applies the headers from showcase/vercel.json and serves 404.html like Vercel does, so the
// Content-Security-Policy is enforced in tests.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { readFileSync } from 'node:fs';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('../showcase/', import.meta.url));
const types = {
  '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.jpg': 'image/jpeg', '.svg': 'image/svg+xml',
  '.glb': 'model/gltf-binary', '.woff2': 'font/woff2', '.wasm': 'application/wasm', '.md': 'text/plain', '.txt': 'text/plain',
};
const escape = text => text.replace(/[.+?^${}()|[\]\\]/g, '\\$&');
const rules = (JSON.parse(readFileSync(join(root, 'vercel.json'), 'utf8')).headers || []).map(rule => ({
  match: new RegExp('^' + rule.source.split('(.*)').map(escape).join('.*') + '$'),
  headers: rule.headers,
}));

export async function startServer() {
  const server = createServer(async (req, res) => {
    const pathname = new URL(req.url, 'http://x').pathname;
    const headers = {};
    for (const rule of rules) if (rule.match.test(pathname)) for (const { key, value } of rule.headers) headers[key] = value;
    let status = 200, file = join(root, normalize(pathname));
    if (file.endsWith('/') || file === root.slice(0, -1)) file = join(file, 'index.html');
    let body;
    try { body = await readFile(file); } catch {
      status = 404; file = join(root, '404.html');
      body = await readFile(file).catch(() => Buffer.from('The page could not be found'));
    }
    res.writeHead(status, { ...headers, 'content-type': types[extname(file)] || 'application/octet-stream' });
    res.end(body);
  }).listen(0, '127.0.0.1');
  await new Promise(r => server.once('listening', r));
  return { base: `http://127.0.0.1:${server.address().port}/`, close: () => server.close() };
}
