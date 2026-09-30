// Fails if a web GLB in showcase/ drifts from its master in exports/.
import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';
import draco3d from 'draco3dgltf';

const TOL = 5e-5; // metres = 0.05 mm
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS).registerDependencies({
  'draco3d.decoder': await draco3d.createDecoderModule(),
});

function stats(doc) {
  const out = new Map();
  for (const mesh of doc.getRoot().listMeshes()) {
    let tris = 0, area = 0;
    const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
    for (const prim of mesh.listPrimitives()) {
      const pos = prim.getAttribute('POSITION'), idx = prim.getIndices();
      const p = i => pos.getElement(i, []);
      const n = idx ? idx.getCount() : pos.getCount();
      for (let i = 0; i < n; i += 3) {
        const v = [0, 1, 2].map(k => p(idx ? idx.getScalar(i + k) : i + k));
        const a = v[1].map((x, d) => x - v[0][d]), b = v[2].map((x, d) => x - v[0][d]);
        area += Math.hypot(a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]) / 2;
        tris++;
      }
      for (let i = 0; i < pos.getCount(); i++) p(i).forEach((x, d) => { min[d] = Math.min(min[d], x); max[d] = Math.max(max[d], x); });
    }
    out.set(mesh.getName(), { tris, area, min, max, mat: mesh.listPrimitives().map(p => p.getMaterial()?.getName()).join() });
  }
  return out;
}

function accessorBounds(accessor) {
  const min = [Infinity, Infinity, Infinity], max = [-Infinity, -Infinity, -Infinity];
  for (let i = 0; i < accessor.getCount(); i++) {
    const v = accessor.getElement(i, []);
    for (let d = 0; d < 3; d++) { min[d] = Math.min(min[d], v[d]); max[d] = Math.max(max[d], v[d]); }
  }
  return { min, max };
}

function checkMaterials(doc, label) {
  const violations = [];
  const meshes = doc.getRoot().listMeshes();
  const badCord = meshes.filter(mesh => /^power__.*__mat_lcd_screen$/.test(mesh.getName()));
  if (badCord.length) violations.push(`${label}: LCD material on power mesh: ${badCord.map(m => m.getName()).join(', ')}`);

  const glass = doc.getRoot().listMaterials().find(material => material.getName() === 'nmc3__nmc3_display__mat_glass_clear');
  if (!glass) violations.push(`${label}: missing nmc3__nmc3_display__mat_glass_clear material`);
  else {
    if (glass.getAlphaMode() !== 'BLEND') violations.push(`${label}: glass alphaMode is ${glass.getAlphaMode()}`);
    if (glass.getBaseColorFactor()[3] >= 1) violations.push(`${label}: glass base-color alpha is opaque`);
  }

  // A bright emissive screen washes out the cream menu text (0.64 did); keep it dim so the menu stays readable.
  const screen = doc.getRoot().listMaterials().find(material => material.getName() === 'nmc3__nmc3_display__mat_lcd_screen');
  if (screen && Math.max(...screen.getEmissiveFactor()) > 0.2) violations.push(`${label}: LCD emissive ${screen.getEmissiveFactor().map(v => v.toFixed(2)).join(', ')} is too bright`);

  for (const mesh of meshes.filter(mesh => mesh.getName() === 'nmc3__nmc3_display__mat_steel_metal')) {
    for (const primitive of mesh.listPrimitives()) {
      const position = primitive.getAttribute('POSITION');
      if (!position) continue;
      const { min, max } = accessorBounds(position);
      const x = max[0] - min[0], y = max[1] - min[1];
      if (Math.abs(x - 0.0284) <= 0.0005 && Math.abs(y - 0.0284) <= 0.0005) {
        violations.push(`${label}: opaque steel display lens bbox ${(x * 1000).toFixed(2)} x ${(y * 1000).toFixed(2)} mm`);
      }
    }
  }
  return violations;
}

if (process.argv.includes('--masters')) {
  let bad = 0;
  for (const n of ['gspe_pdu_apdu9953', 'gspe_pdu_apdu9953_exploded']) {
    const violations = checkMaterials(await io.read(`../exports/apdu9953/glb/${n}.glb`), n);
    if (violations.length) violations.forEach(v => console.log(`VIOLATION ${v}`));
    else console.log(`${n}: material invariants passed`);
    bad += violations.length;
  }
  process.exit(bad ? 1 : 0);
}

let bad = 0;
for (const n of ['gspe_pdu_apdu9953', 'gspe_pdu_apdu9953_exploded']) {
  const master = await io.read(`../exports/apdu9953/glb/${n}.glb`);
  const web = await io.read(`../showcase/${n}.glb`);
  const violations = [...checkMaterials(master, `${n} master`), ...checkMaterials(web, `${n} web`)];
  violations.forEach(v => console.log(`VIOLATION ${v}`));
  bad += violations.length;
  const a = stats(master);
  const b = stats(web);
  let worst = 0, worstArea = 0;
  for (const [name, x] of a) {
    const y = b.get(name);
    const err = y ? Math.max(...x.min.map((v, d) => Math.abs(v - y.min[d])), ...x.max.map((v, d) => Math.abs(v - y.max[d]))) : Infinity;
    worst = Math.max(worst, err);
    const areaErr = y ? Math.abs(x.area - y.area) / x.area : 1;
    worstArea = Math.max(worstArea, areaErr);
    // Area is loose on purpose: sub-millimetre glyphs and contacts move a few percent at 16-bit precision.
    if (!y || x.tris !== y.tris || x.mat !== y.mat || err > TOL || areaErr > 0.03) { bad++; console.log('DRIFT', n, name, y && { tris: [x.tris, y.tris], err, areaErr }); }
  }
  if (a.size !== b.size) { bad++; console.log('MESH COUNT', n, a.size, b.size); }
  console.log(`${n}: ${a.size} meshes, worst bbox error ${(worst * 1000).toFixed(4)} mm, worst area error ${(worstArea * 100).toFixed(2)}%`);
}
process.exit(bad ? 1 : 0);
