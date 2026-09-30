import { NodeIO } from '@gltf-transform/core';
import { ALL_EXTENSIONS } from '@gltf-transform/extensions';

const [oldPath, newPath] = process.argv.slice(2);
if (!oldPath || !newPath) throw new Error('usage: node diff-glb-meshes.mjs <old.glb> <new.glb>');
const io = new NodeIO().registerExtensions(ALL_EXTENSIONS);
const [oldDoc, newDoc] = await Promise.all([io.read(oldPath), io.read(newPath)]);
const oldNames = new Set(oldDoc.getRoot().listMeshes().map(mesh => mesh.getName()));
const newNames = new Set(newDoc.getRoot().listMeshes().map(mesh => mesh.getName()));
for (const name of [...oldNames].filter(name => !newNames.has(name)).sort()) console.log(`- ${name}`);
for (const name of [...newNames].filter(name => !oldNames.has(name)).sort()) console.log(`+ ${name}`);
