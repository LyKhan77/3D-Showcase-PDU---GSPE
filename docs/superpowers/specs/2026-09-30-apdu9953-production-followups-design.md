# APDU9953 production follow-ups

## Objective and current state

The GSPE APDU9953 showcase is live at https://showcase3dpdu-gspe.vercel.app/ and its source is at https://github.com/LyKhan77/3D-Showcase-PDU---GSPE.git (branch `main`, commits `6b40557`, `131e540`, `f804c68`). Vercel imports the repo with Root Directory `showcase`. The smoke test (31 checks), the audit (links, metadata, axe, weight) and the GLB verifier all pass locally and against the live site.

This spec covers what is left. It is written so a fresh session can execute it without the earlier conversation. The owner approved these decisions on 2026-09-30:

| # | Decision | Choice |
|---|---|---|
| D1 | How to fix the wrong materials | Fix the source pipeline (FreeCAD to Blender scripts), re-export the master GLBs |
| D2 | Trademark exposure of NetShelter, NMC3, APDU9953 | Add a disclaimer, keep the product names |
| D3 | `references/` and `previews/socket_ref_large.png` | Stay unpublished |
| D4 | Git LFS | Yes, rewrite history, LFS for `exports/` and `cad/` only |

Success means: the site shows a black cord and a working NMC3 display, every page carries the disclaimer, large binaries live in LFS, `references/` is still absent from GitHub, the repo has a README, and every step has been verified with a command whose output is quoted.

## Task order

The order differs from the first proposal on purpose. LFS goes first so the two new 36 MB master GLBs produced by T1 are never committed to plain git history.

1. **T4 Git LFS migration** (history rewrite, force-push after explicit confirmation)
2. **T2 Disclaimer** (small copy change, one deploy)
3. **T1 Material fixes and master re-export** (needs FreeCAD and Blender, both in `/opt/homebrew/bin`)
4. **T3 References** (no change, only a guard check)
5. **T5 Repo hygiene** (README, real-device check, optional local cleanup)

## T4 Git LFS migration

Scope, by pattern: `exports/**/*.step`, `exports/**/*.glb`, `exports/**/*.FCStd`, `cad/**/*.blend`. That is nine files, about 168 MB. Nothing under `showcase/` moves to LFS. Reason: Vercel builds from `showcase/`, and the deployed GLBs must be real files.

Procedure:
- Require a clean working tree. Make a full backup: `mkdir -p ~/backups && git bundle create ~/backups/3D-Model-PDU-pre-lfs.bundle --all`.
- `git lfs install --local`, then `git lfs migrate import --everything --include="exports/**/*.step,exports/**/*.glb,exports/**/*.FCStd,cad/**/*.blend"`. This rewrites all commits and writes `.gitattributes`.
- Verify: `git lfs ls-files` lists exactly the nine files, `git ls-files showcase | xargs ls -l` shows no LFS pointers, `git count-objects -vH` shrinks, and `git status` is clean.
- **Stop and ask the owner before pushing.** Then `git push --force-with-lease origin main`.
- After the push, confirm the live site still redeploys and passes `BASE_URL=https://showcase3dpdu-gspe.vercel.app/ npm run test:web`.

Risks and checks:
- GitHub LFS free quota is 1 GB storage and 1 GB bandwidth per month. The payload is about 168 MB, so a clone costs that much bandwidth. Tell the owner.
- Vercel must not pull LFS objects on each deploy. The owner checks Project Settings, Git, "Git LFS" is off, because the site does not need them. If it is on, every deploy spends about 168 MB of bandwidth.
- Rollback: the bundle, plus `git reflog` locally. Do not delete the bundle until the live site has been verified.

## T2 Disclaimer

Add one paragraph to the footer of all ten pages (`showcase/index.html`, `showcase/components/*.html` including `index.html`, and `showcase/404.html`):

> NetShelter, NMC and other product names are trademarks of their respective owners. This is an independent 3D study and is not affiliated with or endorsed by them.

Do not name a specific company, since the owner has not confirmed one. Product names, titles and meta tags stay unchanged. Give the paragraph `class="legal"` and add one rule to `showcase/assets/showcase.css` next to the other footer rules (`.footer p` currently sets 14 px `#c6c6c6`): `.footer .legal { margin-top: 16px; max-width: 70ch; color: #8d8d8d; font-size: 12px; }`. Contrast of `#8d8d8d` on the `#161616` footer is about 5.4:1, which passes WCAG AA. Add a `disclaimer` column to `scripts/audit-showcase.mjs` that reports whether each page contains the text, and treat a missing one as a failure.

## T1 Material fixes and master re-export

### Verified root causes

1. **Green cord.** `cad/apdu9953/freecad/modules/sub_top_whip_cord.py:135` colours the cord `(0.045, 0.050, 0.058)`. `find_mat_name` in `cad/apdu9953/freecad/export_mesh_for_blender.py` returns the first material whose colour list has a colour within tolerance 0.03. `mat_lcd_screen` (`LCD_SCREEN = (0.040, 0.050, 0.070)`) appears before `mat_rubber_black`, whose exact colour matches the cord, so the cord becomes `power__main__mat_lcd_screen` with an emissive green. The mesh is 24 x 522 x 24 mm.
2. **White NMC3 display.** `sub_nmc3_controller.py:281` adds `DisplayLens` with colour `(0.700, 0.850, 0.900)`. That colour is listed under `mat_steel_metal`, so the 28.4 x 28.4 mm lens is opaque steel in front of the screen. Hiding that material in the viewer shows the real menu ("Phase Info, Network, Software Info, SKU/Serial #, Display Settings, Log to Flash"). This is the only part that uses that colour.
3. **Output path.** `cad/apdu9953/blender/build_blender_scene.py` writes both GLBs to `SHOWCASE_DIR` (`showcase/`). Running it would overwrite the Draco web copies with 36 MB masters. Masters belong in `exports/apdu9953/glb/`.

### Design

- **Nearest-colour matching.** Change `find_mat_name` to pick the registered colour with the smallest maximum channel difference, still within tolerance 0.03, and to print a warning listing colours that fell through to the `mat_steel_metal` default. Ties keep the earlier material.
- **Glass material.** Add `mat_glass_clear` to `MAT_MAPPING` with colour `(0.700, 0.850, 0.900)`, remove that colour from the steel list, and add a matching spec to `PBR_SPECS` in `build_blender_scene.py`: light blue-grey base colour, alpha about 0.15, roughness about 0.05, metallic 0, blended render mode (Blender 5.2 uses `surface_render_method`; read the enum values from the API before setting them). The exported glTF material must have `alphaMode: "BLEND"` and a base colour alpha below 1.
- **Export location.** Point the GLB output to `exports/apdu9953/glb/`. Keep writing the two `.blend` files to `cad/apdu9953/blender/`. Update the header comment that names `showcase/`.
- **Cache.** After this change the master GLBs change, and returning visitors could keep the old model for up to a day. In `showcase/vercel.json`, shorten the `/gspe_pdu_(.*)` rule to `public, max-age=3600, stale-while-revalidate=86400`.

### Regression check

Extend `scripts/verify-web-glb.mjs` with material invariants on the master GLBs:
- no mesh named `power__*__mat_lcd_screen` exists (the LCD material may appear only under `nmc3__nmc3_display__`),
- `mat_glass_clear` exists on the display, with `alphaMode` `BLEND` and base colour alpha below 1,
- no `nmc3__nmc3_display__mat_steel_metal` mesh has a bounding box of about 28.4 x 28.4 mm.

Acceptance by mesh-name diff between the old and new master GLB: the only differences are `power__main__mat_lcd_screen` becoming `power__main__mat_rubber_black`, and `nmc3__nmc3_display__mat_steel_metal` losing the lens to `nmc3__nmc3_display__mat_glass_clear`. Any other difference must be listed and explained to the owner before continuing. STEP and FCStd are not rebuilt, since only mesh colours change.

### Downstream, in order

`npm run build:web`, `npm run verify:web`, `npm run posters`, regenerate `showcase/assets/og-image.jpg` (the recipe used so far: `sips --resampleHeight 630` on `assets/posters/nmc3.jpg`, then `sips --padToHeightWidth 630 1200 --padColor 111820`; add it to `WORKFLOW.md` or a script so it stops being undocumented), `npm run test:web`, `npm run audit:web`, commit, push, wait for the deploy, then `BASE_URL=https://showcase3dpdu-gspe.vercel.app/ npm run test:web`. Look at `showcase/assets/posters/nmc3.jpg` and `power.jpg`: the display must show the menu, and the cord must be black.

## T3 References

No change. `references/` and `previews/socket_ref_large.png` stay in `.gitignore` with their comment. Guard check at the end: `git ls-files references previews/socket_ref_large.png` prints nothing. Do not delete these files from disk.

## T5 Repo hygiene

- **README.md** at the repo root, under 80 lines: what the project is, the live URL, folder map, the `npm run` commands in `scripts/`, Vercel settings (Root Directory `showcase`, Framework Preset Other, no build command), the LFS note (`git lfs install` before cloning), that `references/` is intentionally absent, the disclaimer, and two caveats: `.mcp.json` and the CAD scripts contain absolute paths for this machine.
- **Real-device check** (owner runs it; the agent provides the checklist and records results): Safari on macOS, Safari on iOS, Chrome on Android. On each: Load 3D, Assembled/Exploded, one stage button, one hotspot tip, one layer toggle. Two 1.2 M-vertex models are heavy on iOS memory, so note any reload or crash.
- **Local cleanup, only after T1 and only with the owner's yes:** `temp/blender_staging_apdu9953/` and `temp/__pycache__/` (part of the 106 MB in `temp/`; T1 recreates the staging files, so keep them until T1 is done) and the root `node_modules/` (18 MB, ignored, no `package.json`). Never delete `temp/prompt/`, which holds the handoff prompts, and never touch `references/`.

## Verification commands

From `scripts/`: `npm run verify:web`, `npm run test:web`, `npm run audit:web`, and the same with `BASE_URL=https://showcase3dpdu-gspe.vercel.app/` for the live site. From the repo root, the FreeCAD tests run with `freecadcmd temp/run_freecad_geometry_tests.py`, and the pure-Python tests with `python3 cad/apdu9953/test_presentation.py` and `python3 cad/apdu9953/test_showcase_contract.py` (pytest is not installed). Exact FreeCAD and Blender invocations for the export steps must be confirmed by reading the scripts and `cad/apdu9953/REFINEMENT.md` first: a likely form is `/opt/homebrew/bin/freecadcmd cad/apdu9953/freecad/export_mesh_for_blender.py` followed by `/opt/homebrew/bin/blender -b --python cad/apdu9953/blender/build_blender_scene.py`. Use the full paths: both tools exist there but were not found on `PATH` in the shell used so far.

## Out of scope

Custom domain, analytics, LOD variants, CI, and self-hosting anything else. If a custom domain is added later, update `og:image`, `og:url` and `canonical` in all pages.
