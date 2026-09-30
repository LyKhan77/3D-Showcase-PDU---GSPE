# APDU9953 geometry parity and GSPE product showcase Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Correct APDU9953 FreeCAD geometry against the OpenSCAD reference, export independently controllable GLB layers, and ship a GSPE branded product landing page plus seven component pages and an NMC3 deep-detail view.

**Architecture:** Keep OpenSCAD as geometry reference and FreeCAD as the B-Rep source. Extend the existing part registry with explicit presentation layers/roles, preserve those identities through OBJ staging and Blender GLB export, then consume them through a shared static showcase shell. `showcase/index.html` is the landing page; shared assets provide the model-viewer controller and page templates; component pages declare data and camera presets rather than duplicating behavior.

**Tech Stack:** Python 3 standard library, FreeCADCmd/Part/Draft, Blender 5.2 Python API, model-viewer 3.5, static HTML/CSS/ES modules, Playwright CLI, Python unittest.

---

## File map

- Modify `cad/apdu9953/freecad/modules/_common.py`: text orientation and shared local-profile helpers.
- Modify `cad/apdu9953/freecad/modules/sub_nmc3_controller.py`: exact RJ45, USB-A, Micro-B, tactile/reset solids and explicit part roles.
- Modify `cad/apdu9953/freecad/modules/sub_breaker_box.py`, `sub_chassis.py`, `sub_socket_bank.py`: text-angle audit and presentation roles for layer export.
- Modify `cad/apdu9953/freecad/pdu_assembly.py`: seven-layer assignment and role metadata.
- Modify `cad/apdu9953/freecad/export_mesh_for_blender.py`: group by layer/role/material and clear stale staging.
- Modify `cad/apdu9953/blender/build_blender_scene.py`: preserve layer metadata and export GLB node/material identities.
- Create `cad/apdu9953/test_freecad_geometry.py`: regression probes for orientation and port geometry; skip cleanly when FreeCAD is unavailable.
- Create `cad/apdu9953/test_showcase_contract.py`: static contract checks for routes, stage data, layers, hotspot coordinates and GSPE branding.
- Create `showcase/assets/showcase.css`: DESIGN.md-derived GSPE layout tokens and responsive components.
- Create `showcase/assets/showcase.js`: shared model, stages, layer visibility, hotspots and page data controller.
- Replace `showcase/index.html`: GSPE product landing page with concise interactive preview and route cards.
- Create `showcase/components/index.html`: seven-module directory.
- Create `showcase/components/housing.html`, `mounting.html`, `power.html`, `breakers.html`, `outlet-banks.html`, `nmc3.html`, `internal-busbars-pcb.html`: shared detail template data and markup.
- Rebuild generated `exports/apdu9953/step/*`, `temp/blender_staging_apdu9953/*`, `showcase/gspe_pdu_apdu9953*.glb` through the supplied commands; do not hand-edit generated assets.
- Create `output/playwright/apdu9953-showcase-check.mjs`: browser smoke flow and screenshot/error capture.

### Task 1: Add failing geometry regression probes

**Files:**
- Create: `cad/apdu9953/test_freecad_geometry.py`
- Modify: none

- [ ] **Step 1: Write failing tests for text orientation and local port profiles.**

```python
import importlib.util
import unittest
from pathlib import Path

FREECAD = importlib.util.find_spec("FreeCAD")

@unittest.skipUnless(FREECAD, "FreeCAD Python modules unavailable")
class GeometryRegression(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from modules._common import make_text_solid
        from modules.sub_nmc3_controller import (
            build_rj45_port, build_usb_micro_port, build_usb_a_port,
        )
        cls.make_text_solid = make_text_solid
        cls.build_rj45_port = build_rj45_port
        cls.build_usb_micro_port = build_usb_micro_port
        cls.build_usb_a_port = build_usb_a_port

    def test_text_positive_local_y_maps_to_positive_model_z(self):
        import FreeCAD as App
        doc = App.newDocument("text_orientation_test")
        shape = self.make_text_solid("GSPE", 6.5, 0.15, 0, 0, 0, doc=doc)
        self.assertGreater(shape.BoundBox.ZMax, shape.BoundBox.ZMin)
        self.assertLess(shape.BoundBox.YMax, 0.01)
        doc.close()

    def test_micro_b_has_trapezoid_width_change(self):
        shape = self.build_usb_micro_port(0, -23, 0)
        self.assertGreater(shape.BoundBox.XLength, 7.5)
        self.assertLess(shape.BoundBox.XLength, 9.0)
        self.assertGreater(shape.BoundBox.ZLength, 2.5)

    def test_universal_io_and_link_port_have_distinct_inversion_bounds(self):
        normal = self.build_rj45_port(0, -23, 0, inverted=False)
        inverted = self.build_rj45_port(0, -23, 0, inverted=True)
        self.assertNotEqual((normal.BoundBox.ZMin, normal.BoundBox.ZMax),
                            (inverted.BoundBox.ZMin, inverted.BoundBox.ZMax))

    def test_usb_a_contains_retention_windows_and_side_detents(self):
        shape = self.build_usb_a_port(0, -23, 0)
        self.assertGreater(shape.Volume, 0)
        self.assertGreater(shape.BoundBox.YLength, 10)

if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and confirm the orientation/inversion assertions fail for the current implementation.**

Run: `rtk python3 -m unittest cad/apdu9953/test_freecad_geometry.py -v`

Expected: the test run skips if the system interpreter lacks FreeCAD; under FreeCADCmd at least the text orientation and RJ45 inversion assertions fail before the implementation changes.

### Task 2: Correct shared text and port solids

**Files:**
- Modify: `cad/apdu9953/freecad/modules/_common.py`
- Modify: `cad/apdu9953/freecad/modules/sub_nmc3_controller.py`
- Modify: `cad/apdu9953/freecad/modules/sub_breaker_box.py`
- Modify: `cad/apdu9953/freecad/modules/sub_socket_bank.py`
- Test: `cad/apdu9953/test_freecad_geometry.py`

- [ ] **Step 1: Change `make_text_solid` to rotate +90 degrees about X and keep extrusion toward -Y.**

Replace the existing placement rotation with:

```python
    # OpenSCAD face_print rotates the local text plane into XZ with +Z up.
    sh.rotate(V(0.0, 0.0, 0.0), V(1.0, 0.0, 0.0), 90.0)
    solid = sh.extrude(V(0.0, -thickness, 0.0))
```

- [ ] **Step 2: Add local-profile helpers for stepped apertures, trapezoid Micro-B shells, wire-between contact segments and signed detents.**

Use exact SCAD dimensions: RJ45 13.4×10, 6.4×2, 3.5×1.5; side windows at X ±9.6; light pipes 3.1×0.35×1.8; USB-A retention windows 2×2.7×1 at X ±4 and detents 0.45×3×1.6 at ±12°; Micro-B outer polygon `[[-4,1.65],[4,1.65],[4,-0.7],[3,-1.65],[-3,-1.65],[-4,-0.7]]`, inner polygon scaled to the SCAD values, 0.6 tongue and five pins.

- [ ] **Step 3: Build each RJ45 subfeature as a separately registered solid.**

Create housing, shell, cavity insert, contact support, eight three-segment wire contacts, side latch windows/seams, light pipes and optional emitters. Apply the 180° rotation only to aperture/insert/contact components for Universal I/O; leave the light-pipe choice controlled by `leds` and use the SCAD invocation with `light_pipes=False` for Universal I/O.

- [ ] **Step 4: Replace full-sphere button domes with flattened clipped domes and add reset plunger.**

Use the ring subtraction and an intersection of a scaled sphere/cube equivalent to the OpenSCAD `nmc_nav_button`; register the reset plunger behind X=-3 mm, Z=24 mm.

- [ ] **Step 5: Audit all vertical labels and outlet numbering.**

Keep `angle_deg=-90.0` where OpenSCAD calls `face_print(...,-90)` and change only if the corrected rendered front close-up shows a reading direction mismatch. Apply the same helper to GSPE, APDU9953, breaker Bank/ON/OFF and socket numbers.

- [ ] **Step 6: Run the FreeCAD regression suite and confirm green.**

Run: `/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd -c "import sys; sys.path.insert(0, 'cad/apdu9953/freecad'); exec(open('cad/apdu9953/test_freecad_geometry.py').read())"`

Expected: all four geometry tests pass with no traceback.

### Task 3: Add explicit seven-layer export metadata

**Files:**
- Modify: `cad/apdu9953/freecad/modules/_common.py`
- Modify: `cad/apdu9953/freecad/pdu_assembly.py`
- Modify: `cad/apdu9953/freecad/export_mesh_for_blender.py`
- Modify: `cad/apdu9953/blender/build_blender_scene.py`
- Test: `cad/apdu9953/test_showcase_contract.py`

- [ ] **Step 1: Define stable layer IDs and role assignment.**

Add `LAYER_*` constants for `housing`, `mounting`, `power`, `breakers`, `outlet_banks`, `nmc3`, and `internal`. Extend `P(parts, ...)` with optional `layer` and `role` values while keeping existing positional callers valid. Assign internal busbars, relay PCBs, socket contacts and NMC PCB/tray to `internal`; breaker bodies and breaker controls to `breakers`; fasteners inherit the retained component layer.

- [ ] **Step 2: Update mesh grouping to include layer, role and material.**

Replace the current six-group key with `layer__role__material`, clear `temp/blender_staging_apdu9953` before exporting assembled and exploded states, and write a `manifest.json` containing layer IDs, source part names, bounds and material IDs. Fail the export when a part has no layer.

- [ ] **Step 3: Preserve layer names in Blender parent empties and GLB nodes/materials.**

Create seven named empties and attach each imported mesh to its layer. Keep material names unique per layer/role where the same source material would otherwise be shared. Export both GLBs with `extras` metadata on layer empties containing `layerId`, display label and source state.

- [ ] **Step 4: Add contract tests for the manifest and HTML layer IDs.**

`test_showcase_contract.py` must assert the manifest has exactly the seven layer IDs, each GLB path exists after rebuild, and `showcase/assets/showcase.js` contains the same IDs. Run this test after asset generation, not before.

### Task 4: Rebuild and validate CAD/mesh/GLB pipeline

**Files:**
- Modify: `cad/apdu9953/freecad/build_step.py` only if logging or output validation needs the new manifest.
- Modify: `cad/apdu9953/freecad/export_mesh_for_blender.py`.
- Modify: `cad/apdu9953/blender/build_blender_scene.py`.
- Generate: `exports/apdu9953/step/*`, `temp/blender_staging_apdu9953/*`, `showcase/gspe_pdu_apdu9953*.glb`.

- [ ] **Step 1: Build native FreeCAD and STEP outputs.**

Run: `/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd cad/apdu9953/freecad/build_step.py`

Expected: `BUILD STEP COMPLETE SUCCESS`, updated `gspe_pdu_apdu9953.step` and `.FCStd`, and no missing-object traceback.

- [ ] **Step 2: Re-tessellate both staging states.**

Run: `/Applications/FreeCAD.app/Contents/Resources/bin/FreeCADCmd cad/apdu9953/freecad/export_mesh_for_blender.py`

Expected: assembled and exploded directories contain non-empty OBJ files for every layer, plus `manifest.json` with bounds.

- [ ] **Step 3: Bake PBR and export both GLBs.**

Run: `/Applications/Blender.app/Contents/MacOS/Blender --background --python cad/apdu9953/blender/build_blender_scene.py`

Expected: both GLBs and corresponding `.blend` files update; Blender exits 0 with no skipped-object errors.

- [ ] **Step 4: Validate generated assets structurally.**

Run: `rtk python3 - <<'PY'` with a script that loads both GLB JSON chunks, asserts `asset.version == "2.0"`, checks all seven layer IDs in node names/extras, checks finite bounds with Z height spanning approximately 0 to 1.829 m for assembled chassis, and checks material names include `NMC3`, `INTERNAL`, `BREAKERS`, `OUTLET_BANKS` role prefixes.

Expected: `GLB CONTRACT PASS assembled exploded`.

### Task 5: Build shared GSPE landing/detail frontend shell

**Files:**
- Create: `showcase/assets/showcase.css`
- Create: `showcase/assets/showcase.js`
- Replace: `showcase/index.html`
- Create: `showcase/components/index.html`
- Create: `showcase/components/housing.html`
- Create: `showcase/components/mounting.html`
- Create: `showcase/components/power.html`
- Create: `showcase/components/breakers.html`
- Create: `showcase/components/outlet-banks.html`
- Create: `showcase/components/nmc3.html`
- Create: `showcase/components/internal-busbars-pcb.html`

- [ ] **Step 1: Add a static contract test before markup.**

Write `test_showcase_contract.py` assertions that the landing contains `GSPE`, `APDU9953`, the seven required component links and no `IBM` string; each component page contains a breadcrumb, `model-viewer`, a shared CSS/JS reference and a canonical component ID; `nmc3.html` contains `RJ45`, `USB-A`, `Micro-B`, `Display`, `PCB`, and `Shielding tray`.

- [ ] **Step 2: Implement `showcase.css` from DESIGN.md tokens.**

Define GSPE navy/cream and Carbon-derived canvas/surface/hairline tokens; IBM Plex Sans import/fallback; square controls/cards; 4px spacing; 48px touch targets; responsive breakpoints at 1056px, 672px and 320px; dark viewport surface; light landing shell; focus-visible ring; reduced-motion media rule.

- [ ] **Step 3: Implement shared `showcase.js` data and controller.**

Define `COMPONENTS`, `LAYERS`, `STAGES`, and `HOTSPOTS` data. On `model-viewer` load, resolve layer names from public scene graph/material API, cache original material alpha/color, and set visibility per layer without changing unrelated layers. Apply pending stage state after source changes. Use `cameraOrbit`/`cameraTarget` with smooth interpolation, stop autorotate on interaction, and expose `setStage`, `setLayerVisibility`, `setModelMode`, and `focusHotspot` for page markup.

- [ ] **Step 4: Implement landing page structure.**

Build GSPE header, product hero, key rating strip, dark assembled preview, “Explore the system” action, seven component cards, seven-stage overview and footer. Keep full inspection controls behind the primary action or a clearly labeled “Open interactive inspection” link.

- [ ] **Step 5: Implement directory and detail page template.**

Use declarative `data-component` attributes to populate title, role, specs, model source, camera preset and previous/next links. Keep one reusable detail layout with component viewer, assembled/exploded/isolate controls, spec card, integration section and breadcrumb. NMC3 adds port family tabs and the dedicated detail section.

### Task 6: Add stable hotspots and responsive interaction behavior

**Files:**
- Modify: `showcase/assets/showcase.css`
- Modify: `showcase/assets/showcase.js`
- Modify: all pages containing `model-viewer` hotspots
- Create: `output/playwright/apdu9953-showcase-check.mjs`

- [ ] **Step 1: Define hotspot records in metres from exported manifest.**

Use chassis-derived Z values: NMC3 0.9145 m, outlet bank centers 1.1595/0.6695/0.3295 m, breakers 1.3295/0.4995 m, rear mounting 1.7545 m, ground point 0.150 m; use actual manifest bounds for plug/cable height rather than the current hard-coded 2.100 m.

- [ ] **Step 2: Implement one tooltip card with safe-area clamping.**

Project each hotspot with `modelViewer.positionAndNormalFromPoint`, choose the side with available room, clamp card rectangle to viewport padding, and move a CSS triangle pointer to the projected anchor. Recompute on `camera-change`, resize, source load and layer changes. Hide cards when their layer is off or the hotspot is outside the viewport.

- [ ] **Step 3: Implement stage descriptions and horizontal timeline.**

Render stage title, technical summary, current index and previous/next controls from `STAGES`. Stage selection updates model source, camera and layer preset as one atomic state transition; manual layer edits add a visible “Customized view” label.

- [ ] **Step 4: Run the browser smoke flow and capture screenshots.**

The Playwright CLI script must open landing, click interactive inspection, select stages 1 through 7, toggle each of seven layers off/on, open every component route, open NMC3 tabs, switch assembled/exploded, resize to 390px and 1440px widths, and collect console/page errors. Save screenshots under `output/playwright/` and exit nonzero on errors or missing required text.

### Task 7: Verification and handoff

**Files:**
- Modify: `cad/apdu9953/test_showcase_contract.py` only for verified contract changes.
- Create: `output/apdu9953-verification.md`.

- [ ] **Step 1: Run geometry tests and existing showcase tests.**

Run: `rtk python3 -m unittest cad/apdu9953/test_showcase.py cad/apdu9953/test_freecad_geometry.py cad/apdu9953/test_showcase_contract.py -v`

Expected: all runnable tests pass; FreeCAD-specific tests report an explicit skip only when invoked outside FreeCADCmd.

- [ ] **Step 2: Run the browser smoke flow.**

Run: `rtk node output/playwright/apdu9953-showcase-check.mjs`

Expected: all routes/stages/layers pass, screenshots exist, and no uncaught browser errors appear.

- [ ] **Step 3: Inspect visual artifacts.**

Open the desktop and mobile screenshots. Confirm GSPE branding, no IBM text, square Carbon-style chrome, readable product hierarchy, no overlap, stable tooltip pointers, and accurate stage/model transitions.

- [ ] **Step 4: Write verification evidence.**

Record command outputs, generated file sizes, GLB contract results, browser screenshot paths, and any limits in `output/apdu9953-verification.md`. Do not claim completion while any required command or browser path is failing.

## Plan self-review

- Geometry parity is covered by Tasks 1–2, including all requested NMC3 microfeatures and text directions.
- Layer independence and generated GLBs are covered by Tasks 3–4.
- Landing page, seven component pages, NMC3 deep detail and GSPE/`DESIGN.md` styling are covered by Task 5.
- Stage timeline, camera state, hotspot coordinates, tooltip clamping and responsive behavior are covered by Task 6.
- Automated and visual verification are covered by Task 7.
- No Git commit steps are included because this workspace has no `.git` directory.

Plan complete and saved locally. Implementation requires choosing execution mode before code changes.
