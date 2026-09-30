#!/bin/sh
# Master GLBs in exports/ stay full detail. This writes Draco copies for the web into showcase/.
# Position 16-bit = about 0.03 mm on a 1.8 m mesh, normals 12-bit. Run `npm run verify:web` after.
set -e
cd "$(dirname "$0")"
for n in gspe_pdu_apdu9953 gspe_pdu_apdu9953_exploded; do
  ./node_modules/.bin/gltf-transform draco "../exports/apdu9953/glb/$n.glb" "../showcase/$n.glb" \
    --quantize-position 16 --quantize-normal 12
done
