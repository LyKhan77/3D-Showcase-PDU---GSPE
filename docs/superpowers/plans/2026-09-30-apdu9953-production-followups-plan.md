# APDU9953 production follow-ups Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline, in this session) to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. The owner chose inline execution.

**Goal:** Finish the APDU9953 showcase: move large binaries to Git LFS, add a trademark disclaimer, fix the wrong cord and display-lens materials in the CAD-to-GLB pipeline, redeploy, and leave the repo documented.

**Architecture:** Five ordered tasks. Task 3 is test-first: material invariants for the master GLBs fail first, then the FreeCAD and Blender scripts are fixed until they pass. Masters live in `exports/apdu9953/glb/`. Task 4 rebuilds the web copies in `showcase/` from them and deploys.

**Tech Stack:** git and git-lfs 3.7.1, Node 24 with the `scripts/` npm project (glTF Transform, Playwright), FreeCAD (`/opt/homebrew/bin/freecadcmd`), Blender 5.2 (`/opt/homebrew/bin/blender`), static HTML/CSS/ES modules on Vercel.

**Spec:** `docs/superpowers/specs/2026-09-30-apdu9953-production-followups-design.md` (read it first; it holds the evidence for every root cause).

## Global Constraints

- Live site `https://showcase3dpdu-gspe.vercel.app/`; repo `https://github.com/LyKhan77/3D-Showcase-PDU---GSPE.git`, branch `main`; Vercel Root Directory is `showcase`.
- LFS patterns, exactly: `exports/**/*.step`, `exports/**/*.glb`, `exports/**/*.FCStd`, `cad/**/*.blend`. Nothing under `showcase/` goes to LFS.
- Disclaimer text, exactly: `NetShelter, NMC and other product names are trademarks of their respective owners. This is an independent 3D study and is not affiliated with or endorsed by them.` Name no company.
- Master GLBs are written to `exports/apdu9953/glb/`, `.blend` files to `cad/apdu9953/blender/`. Never write masters into `showcase/`.
- GLB cache rule in `showcase/vercel.json` becomes `public, max-age=3600, stale-while-revalidate=86400`.
- `references/` and `previews/socket_ref_large.png` stay unpublished and are never deleted from disk.
- Ask the owner before: any push that rewrites history, and any deletion of local files.
- Call FreeCAD and Blender by full path. pytest is not installed; use `unittest` runners.
- Follow the harness's commit attribution rules on every commit. Scripts under `scripts/` and the Playwright tests need network.
- Spec and plan commits are local until Task 1 pushes; do not push before Task 1 completes.

## Review Focus

1. **Vercel pulls LFS objects on every deploy** (about 168 MB each): Task 1 step 7 makes the owner check Project Settings, Git, "Git LFS" is off.
2. **Returning visitors keep the old GLB** for up to a day: Task 4 changes the cache rule and step 7 checks the live header.
3. **Nearest-colour matching silently reassigns other parts' materials:** Task 3 step 7 diffs mesh names between the old and new masters and stops on any unexpected line.
4. **The glass alpha is lost on export, or the layer toggle in `showcase.js` resets it:** Task 3 asserts `alphaMode` and alpha in the GLB, Task 4 asserts alpha in the browser before and after toggling the NMC3 layer.
5. **Force-push overwrites remote work made elsewhere:** Task 1 step 1 requires `origin/main` to be an ancestor of local `main`, and the push uses `--force-with-lease`.

---

### Task 1: Git LFS migration

**Files:**
- Create (by the tool): `.gitattributes`
- Modify: git history of `main` and `origin/main`

**Interfaces:**
- Produces: `.gitattributes` with four `filter=lfs` lines for the patterns in Global Constraints; nine LFS files (`exports/apdu9953/{glb x2, step, FCStd}`, `exports/apdu11590sm/{glb, step, FCStd}`, `cad/apdu9953/blender/*.blend` x2).

- [ ] **Step 1: Preconditions**
Run `git status --short` (expect empty), `git lfs version` (expect `git-lfs/3.x`), then `git fetch origin && git status -sb` (expect `## main...origin/main [ahead 2]`, the spec and plan commits) and `git merge-base --is-ancestor origin/main main && echo ok` (expect `ok`). If any differs, stop and ask the owner.

- [ ] **Step 2: Record the baseline**
Run `git lfs ls-files` (expect no output) and `git count-objects -vH | grep size-pack`; note the size.

- [ ] **Step 3: Back up**
Run `mkdir -p ~/backups && git bundle create ~/backups/3D-Model-PDU-pre-lfs.bundle --all && git bundle verify ~/backups/3D-Model-PDU-pre-lfs.bundle` (expect `is okay`).

- [ ] **Step 4: Migrate**
Run `git lfs install --local`, then `git lfs migrate import --everything --include="exports/**/*.step,exports/**/*.glb,exports/**/*.FCStd,cad/**/*.blend"`. Expect each commit rewritten and `git lfs ls-files` listing exactly the nine files; `.gitattributes` has four lines; `git status --short` is empty.

- [ ] **Step 5: Verify nothing else moved**
Run `for f in $(git ls-files showcase); do head -c 40 "$f" | grep -q "git-lfs" && echo "POINTER $f"; done` (expect no output) and `ls -l exports/apdu9953/glb/*.glb` (expect about 36 MB each, real files in the working tree).

- [ ] **Step 6: Get the owner's confirmation, then push**
Tell the owner: history was rewritten, about 168 MB now goes to GitHub LFS, the free quota is 1 GB storage and 1 GB bandwidth per month. Wait for an explicit yes. Then `git push --force-with-lease origin main` (expect `forced update`), and `git ls-remote origin` shows the local `main` hash.

- [ ] **Step 7: Verify the deploy still works**
Wait for the Vercel deploy, then from `scripts/` run `BASE_URL=https://showcase3dpdu-gspe.vercel.app/ npm run test:web` (expect `all passed`). Ask the owner to confirm in Vercel, Project Settings, Git, that "Git LFS" is off and that the deploy log shows no LFS download. Keep `~/backups/3D-Model-PDU-pre-lfs.bundle` until then.

---

### Task 2: Trademark disclaimer

**Files:**
- Modify: `scripts/audit-showcase.mjs`, `showcase/assets/showcase.css`, `showcase/index.html`, `showcase/404.html`, `showcase/components/index.html`, `showcase/components/{housing,mounting,power,breakers,outlet-banks,nmc3,internal-busbars-pcb}.html`

**Interfaces:**
- Produces: the audit's per-page info gains `disclaimer: boolean` and prints `disclaimer:true|false` in the metadata section; the audit exits with code 1 when any page has `false`. Each page footer gains `<p class="legal">…</p>` with the exact text from Global Constraints.

- [ ] **Step 1: Write the failing check**
In `audit-showcase.mjs`, inside the `page.evaluate` that builds `info`, add `disclaimer: document.body.innerText.includes('independent 3D study')`. Print it in the metadata line and, after the loop, set `process.exitCode = 1` if any `problems` entry has `disclaimer === false`.

- [ ] **Step 2: Run it and see it fail**
From `scripts/`: `node audit-showcase.mjs; echo "exit=$?"`. Expect `disclaimer:false` on all ten pages and `exit=1`.

- [ ] **Step 3: Add the paragraph and the style**
Insert `<p class="legal">TEXT</p>` before `</footer>` in the ten pages (one scripted replace over the list). Add `.footer .legal { margin-top: 16px; max-width: 70ch; color: #8d8d8d; font-size: 12px; }` after the `.footer p` rule in `showcase.css`. Check `grep -c 'class="legal"'` returns 1 for every page.

- [ ] **Step 4: Run it and see it pass**
`node audit-showcase.mjs; echo "exit=$?"`. Expect `disclaimer:true` everywhere, `axe violations: none`, no `OVERFLOW-X`, `exit=0`. Look at the footer once with a Playwright screenshot at 390 px width.

- [ ] **Step 5: Commit and deploy**
`git add scripts/audit-showcase.mjs showcase && git commit -m "feat: add trademark disclaimer to all pages"`, `git push`. After the deploy, `BASE_URL=https://showcase3dpdu-gspe.vercel.app/ node audit-showcase.mjs; echo "exit=$?"` expects `exit=0`.

---

### Task 3: Fix materials in the pipeline and re-export the masters

**Files:**
- Modify: `scripts/verify-web-glb.mjs`, `cad/apdu9953/freecad/export_mesh_for_blender.py`, `cad/apdu9953/blender/build_blender_scene.py`
- Create: `scripts/diff-glb-meshes.mjs`
- Regenerated: `exports/apdu9953/glb/gspe_pdu_apdu9953.glb`, `exports/apdu9953/glb/gspe_pdu_apdu9953_exploded.glb`, `cad/apdu9953/blender/*.blend`

**Interfaces:**
- Produces in JS: `checkMaterials(doc: Document, label: string): string[]` (violations, empty means ok), called on both master GLBs; `verify-web-glb.mjs --masters` runs only these checks. `diff-glb-meshes.mjs <old.glb> <new.glb>` prints `- name` or `+ name` for each mesh-name difference, exit 0.
- Produces in Python: `find_mat_name(color: tuple[float, float, float]) -> str`, nearest registered colour within tolerance 0.03 (ties keep the earlier material), default `"mat_steel_metal"` with a printed warning that lists the unmatched colours; `MAT_MAPPING["mat_glass_clear"] = [(0.700, 0.850, 0.900)]` and that colour removed from the `mat_steel_metal` list; `PBR_SPECS["mat_glass_clear"]`.

- [ ] **Step 1: Snapshot the current masters**
`mkdir -p temp/master-glb-before && cp exports/apdu9953/glb/gspe_pdu_apdu9953*.glb temp/master-glb-before/` (`temp/` is git-ignored). Expect two files of about 36 MB.

- [ ] **Step 2: Write the failing invariants**
In `verify-web-glb.mjs` implement `checkMaterials` returning a message for each violation of:
  1. a mesh named `/^power__.*__mat_lcd_screen$/` exists;
  2. `nmc3__nmc3_display__mat_glass_clear` is missing, or its material `getAlphaMode() !== 'BLEND'`, or `getBaseColorFactor()[3] >= 1`;
  3. a mesh `nmc3__nmc3_display__mat_steel_metal` exists whose POSITION min/max extents in X and Y are both within 0.5 mm of 28.4 mm.
Add the `--masters` flag and a call on both master GLBs. Also create `diff-glb-meshes.mjs` (read both files with `NodeIO`, compare sets of `mesh.getName()`).

- [ ] **Step 3: Run and see them fail**
`node verify-web-glb.mjs --masters; echo "exit=$?"` from `scripts/`. Expect violations 1, 2 and 3 for both GLBs and `exit=1`. Also `node diff-glb-meshes.mjs ../temp/master-glb-before/gspe_pdu_apdu9953.glb ../temp/master-glb-before/gspe_pdu_apdu9953.glb` prints nothing and exits 0.

- [ ] **Step 4: Implement `find_mat_name` and the glass mapping**
In `export_mesh_for_blender.py` compute, per registered colour, the largest per-channel difference, choose the minimum within tolerance 0.03, and warn about fall-throughs. Add `mat_glass_clear` to `MAT_MAPPING` and drop `(0.700, 0.850, 0.900)` from the steel list.

- [ ] **Step 5: Add the glass material to Blender**
In `build_blender_scene.py` add `PBR_SPECS["mat_glass_clear"]`: light blue-grey base colour `(0.700, 0.850, 0.900, 1.0)`, alpha about 0.15, roughness about 0.05, metallic 0, blended render mode. Follow how the existing specs are consumed and add whatever key the material builder needs for alpha. Read the valid enum values for the render mode from `bpy.types.Material.bl_rna.properties` before assigning (Blender 5.2 uses `surface_render_method`).

- [ ] **Step 6: Redirect the output and re-export**
Change the GLB output directory from `SHOWCASE_DIR` to `exports/apdu9953/glb/` (create it if missing) and fix the header comment that names `showcase/`. Read `cad/apdu9953/REFINEMENT.md` for the run commands, then run `/opt/homebrew/bin/freecadcmd cad/apdu9953/freecad/export_mesh_for_blender.py` followed by `/opt/homebrew/bin/blender -b --python cad/apdu9953/blender/build_blender_scene.py`. Expect `Selesai assembled`, `Selesai exploded`, and two `Exported GLB: …/exports/apdu9953/glb/…` lines. Confirm `ls -l showcase/*.glb` still shows the two 2.2 MB Draco files and that `git status --short showcase` is empty.

- [ ] **Step 7: Verify the result**
Run `node verify-web-glb.mjs --masters` (expect no violations, `exit=0`). Run `node diff-glb-meshes.mjs ../temp/master-glb-before/gspe_pdu_apdu9953.glb ../exports/apdu9953/glb/gspe_pdu_apdu9953.glb` and the same for the `_exploded` pair. Expected output is `- power__main__mat_lcd_screen`, `- nmc3__nmc3_display__mat_steel_metal`, `+ nmc3__nmc3_display__mat_glass_clear`, and `+ power__main__mat_rubber_black` unless that mesh already existed in the old file. Any other line: stop and show the owner before continuing.

- [ ] **Step 8: Run the CAD tests**
From the repo root: `/opt/homebrew/bin/freecadcmd temp/run_freecad_geometry_tests.py` (expect 6/6 pass), `python3 cad/apdu9953/test_presentation.py`, `python3 cad/apdu9953/test_showcase_contract.py` (expect pass). Fix only failures caused by this task.

- [ ] **Step 9: Commit (do not push yet)**
`git add scripts cad exports && git commit -m "fix: correct cord and display-lens materials, write masters to exports/"`. The GLBs and `.blend` files are stored through LFS.

---

### Task 4: Rebuild web assets and deploy

**Files:**
- Modify: `scripts/test-showcase.mjs`, `showcase/vercel.json`, `WORKFLOW.md`
- Create: `scripts/make-og-image.sh`
- Regenerated: `showcase/gspe_pdu_apdu9953.glb`, `showcase/gspe_pdu_apdu9953_exploded.glb`, `showcase/assets/posters/*.jpg`, `showcase/assets/og-image.jpg`

**Interfaces:**
- Consumes: the master GLBs from Task 3.
- Produces: `sh scripts/make-og-image.sh` writes `showcase/assets/og-image.jpg` at 1200 x 630 from `showcase/assets/posters/nmc3.jpg` (`sips --resampleHeight 630`, then `sips --padToHeightWidth 630 1200 --padColor 111820`); a test helper `glassAlpha(page): Promise<number>` in `test-showcase.mjs`.

- [ ] **Step 1: Write the failing browser check**
In the `nmc3` component-page flow of `test-showcase.mjs`, after the model loads, read the base colour alpha of the material named `nmc3__nmc3_display__mat_glass_clear` from `viewer.model.materials`. Assert it is below 1. Then uncheck and re-check `[data-layer="nmc3"]` and assert the alpha equals the value from before the toggle.

- [ ] **Step 2: Run and see it fail**
`node test-showcase.mjs 2>&1 | grep -E "FAIL|passed"`. Expect a FAIL on the glass check, because the web copies are still the old ones.

- [ ] **Step 3: Rebuild the web GLBs**
`npm run build:web` (expect two files of about 2.2 MB), then `npm run verify:web` (expect masters invariants clean, both web GLBs within 0.05 mm bounding-box error and 3% area error, `exit=0`).

- [ ] **Step 4: Regenerate posters and the OG image**
`npm run posters`, then create and run `scripts/make-og-image.sh` and add one line about it to the `WORKFLOW.md` Tahap 6 block. Check `sips -g pixelWidth -g pixelHeight showcase/assets/og-image.jpg` prints 1200 and 630. Read `showcase/assets/posters/nmc3.jpg` (the display must show "Phase Info" and the menu) and `power.jpg` (the cord must be black); tell the owner what you saw.

- [ ] **Step 5: Change the GLB cache rule**
In `showcase/vercel.json` set the `/gspe_pdu_(.*)` value to `public, max-age=3600, stale-while-revalidate=86400`. Run `python3 -c "import json;json.load(open('showcase/vercel.json'))"` (expect no error).

- [ ] **Step 6: Run everything locally**
From `scripts/`: `npm run test:web` (expect `all passed`, including the glass checks) and `npm run audit:web` (expect `none` for axe and `exit=0`).

- [ ] **Step 7: Commit, deploy, verify live**
`git add showcase scripts WORKFLOW.md && git commit -m "feat: rebuild web assets with corrected materials, shorten GLB cache"`, `git push` (a normal push). After the deploy: `BASE_URL=https://showcase3dpdu-gspe.vercel.app/ npm run test:web` (expect `all passed`); fetch `/gspe_pdu_apdu9953.glb` and expect `cache-control: public, max-age=3600, stale-while-revalidate=86400`; `/assets/og-image.jpg` returns 200. Ask the owner to hard-refresh the site and confirm a black cord and a readable display.

---

### Task 5: Repo hygiene and final verification

**Files:**
- Create: `README.md`

**Interfaces:**
- Consumes: the commands and paths from Tasks 1 to 4.
- Produces: a root README under 80 lines, covering: what the project is, the live URL, folder map, the `npm run` commands in `scripts/`, Vercel settings (Root Directory `showcase`, Framework Preset Other, no build command, Git LFS off), the LFS note (`git lfs install` before cloning), that `references/` is intentionally absent, the disclaimer text, and two caveats: `.mcp.json` and the CAD scripts contain absolute paths for this machine.

- [ ] **Step 1: Write the README**
Create it, then `wc -l README.md` (expect under 80).

- [ ] **Step 2: Guard the references decision**
`git ls-files references previews/socket_ref_large.png` prints nothing, and `git check-ignore -v references previews/socket_ref_large.png` shows both matched in `.gitignore`.

- [ ] **Step 3: Give the owner the real-device checklist**
Print it and ask the owner to report results: Safari on macOS, Safari on iOS, Chrome on Android; on each, Load 3D, Assembled/Exploded, one stage button, one hotspot tip, one layer toggle; note any reload or crash. Record the answer in the final report; do not write it to the repo.

- [ ] **Step 4: Offer local cleanup, only with a yes**
Show `du -sh temp/blender_staging_apdu9953 temp/__pycache__ node_modules`. If the owner agrees, delete only those three paths. Never delete `temp/prompt/` (it holds the handoff prompts) or `references/`.

- [ ] **Step 5: Commit, push and run the final suite**
`git add README.md && git commit -m "docs: add README"`, `git push`. Then, from `scripts/`: `npm run verify:web`, `npm run test:web`, `npm run audit:web`, and the last two again with `BASE_URL=https://showcase3dpdu-gspe.vercel.app/`. From the repo root: `git status --short` is empty and `git lfs ls-files` lists nine files. Report each result with its output, not from memory.

## Erratum (2026-09-30)

Wherever this plan or the spec says `/opt/homebrew/bin/blender`, use `/Applications/Blender.app/Contents/MacOS/Blender` instead. See the spec's erratum.
