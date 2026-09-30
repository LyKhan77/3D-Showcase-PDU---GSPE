# GSPE APDU9953 3D Showcase

Engineering 3D study of a 24-outlet switched rack PDU with NMC3 management.

Live showcase: https://showcase3dpdu-gspe.vercel.app/

## Repository map

- `cad/apdu9953/` — FreeCAD export and Blender scene pipeline.
- `exports/apdu9953/` — production STEP/FCStd and full-detail GLB masters (Git LFS).
- `showcase/` — static Vercel site and Draco web GLBs.
- `scripts/` — web build, verification, poster, smoke, and audit commands.
- `specs/` and `libraries/` — parameter and standard references.
- `references/` is intentionally absent from Git and remains unpublished.

## Web commands

Run from `scripts/`:

```sh
npm install
npm run build:web
npm run verify:web
npm run posters
sh make-og-image.sh
npm run test:web
npm run audit:web
```

`build:web` reads masters from `exports/` and writes compressed copies to `showcase/`.
`verify:web` checks mesh bounds, materials, glass alpha, and master/web parity.

## Deployment

Vercel uses Root Directory `showcase`, Framework Preset `Other`, no build command, and Git LFS disabled. The GLB cache is one hour with stale-while-revalidate for one day. The master binaries require Git LFS; run `git lfs install` before cloning or pulling this repository.

The pages include this notice: “NetShelter, NMC and other product names are trademarks of their respective owners. This is an independent 3D study and is not affiliated with or endorsed by them.”

The project MCP configuration and CAD scripts contain absolute paths for the author’s machine. Update those paths before moving the pipeline to another workstation.
