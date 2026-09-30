// Minimal static server for showcase/, used by the poster and smoke-test scripts.
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

export const root = fileURLToPath(new URL('../showcase/', import.meta.url));
const types = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.jpg': 'image/jpeg', '.glb': 'model/gltf-binary' };

export async function startServer() {
  const server = createServer(async (req, res) => {
    try {
      const p = join(root, normalize(new URL(req.url, 'http://x').pathname));
      const body = await readFile(p.endsWith('/') ? p + 'index.html' : p);
      res.writeHead(200, { 'content-type': types[extname(p)] || 'application/octet-stream' });
      res.end(body);
    } catch { res.writeHead(404).end(); }
  }).listen(0, '127.0.0.1');
  await new Promise(r => server.once('listening', r));
  return { base: `http://127.0.0.1:${server.address().port}/`, close: () => server.close() };
}
