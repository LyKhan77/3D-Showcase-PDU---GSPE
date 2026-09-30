# APDU9953 geometry parity and horizontal showcase

## Objective and references

Bring the specified FreeCAD details into agreement with the local OpenSCAD gold standard, rebuild the native/STEP and both production GLB assets, and replace the overlapping showcase controls with a horizontal presentation timeline. The user selected the horizontal timeline in the visual companion on 2026-09-30.

The assembly and `openscad/modules/sub_nmc3_controller.scad` define geometry, layout and port orientation. `detail_common.scad` defines text orientation. Existing reference limitations in `cad/apdu9953/REFINEMENT.md` remain applicable: parity means agreement with this reconstruction, not manufacturer-certified dimensions.

## Geometry

Use millimetres throughout FreeCAD: X across the fascia, negative Y toward the viewer, Z upward from 0 to 1829 mm for the chassis. Map the text's positive local Y to positive model Z using +90 degrees about X, and extrude toward negative Y. Keep local text angles consistent with OpenSCAD `face_print`, including -90 degrees for vertical legends unless comparison identifies a differing reference angle. Audit branding, breakers, NMC3, and outlet numbering visually.

Repair `polygon_prism_xz` so the input polygon's Z coordinates are preserved while extrusion remains toward positive Y; its current negative-X rotation reflects asymmetric XZ profiles. Audit callers before changing the helper.

Build NMC3 ports in local coordinates, transform inverted features around the local Y axis, then translate to their assembly centers. This avoids inversion around a world-space depth offset. Keep housing, metal shell, insulator, contacts, light pipes and emitters as separate colored registered solids so PBR can preserve material differences.

RJ45 parity includes the stepped aperture, reference housing bevel and aperture clearance, recessed insert, eight three-segment cylindrical wires, sloped support, bearing ledges, side latch windows, retention folds and diagonal seams. Universal I/O flips the aperture/insert/contact assembly by 180 degrees and has no light pipes, matching the actual SCAD invocation. Link A/B have neutral lenses; Network includes green/amber emitters behind the lenses.

USB-A parity includes its hollow rounded shell, two top retention windows, side detents rotated by signed 12-degree angles, cream tongue, four gold contacts and rear insulating stop. Preserve the rectangular contact geometry in the SCAD reference; do not invent unspecified pin notches.

Micro-B uses the exact outer and inner six-point polygons from OpenSCAD, a 0.6 mm tongue and five gold pins. Navigation buttons use separate rings and flattened, clipped domes matching the reference rather than full spheres. Add the reset plunger behind the X=-3 mm pinhole.

## Showcase composition

Use `DESIGN.md` as the visual source of truth for the interactive web showcase. Keep its Carbon-inspired discipline while changing all IBM branding, marks and copy to GSPE. The shell uses a light canvas, light-gray alternate surfaces, charcoal text, square corners, 1px hairlines, 4px spacing grid, and IBM Plex Sans with weight 300 for large display text and weight 400 for body text. GSPE navy `#003674` replaces IBM Blue as the primary accent, GSPE cream `#FAFFD8` marks product emphasis, and semantic green/yellow/red remain status colors. Do not add IBM wordmarks or IBM product language.

The 3D viewport is an intentional product surface: it remains dark so the APDU9953 model and its GSPE accent details retain contrast. Viewport controls follow the same flat Carbon treatment: square buttons, hairline borders, no atmospheric gradients or drop shadows. The surrounding page, timeline, cards and layer manager follow `DESIGN.md`'s light, flat system.

Organize the application into normal layout regions rather than competing floating overlays:

- A compact GSPE top header for branding, product facts and utility controls. Use GSPE wordmark/text treatment only.
- A large central viewport, with its own small camera toolbar and loading/error states.
- A lower presentation area for stage number, technical summary, previous/next controls, and the seven-step horizontal timeline.
- A collapsible layer panel allocated outside the viewport on desktop. On small screens, it expands into a dedicated layout region and the timeline scrolls horizontally.

Desktop keeps the header, model, summary and timeline visible without overlap. Mobile reserves useful viewport height and allows page/panel scrolling where necessary. Respect reduced motion, provide focus-visible styling, readable contrast and accessible switch/button labels. Keep all interactive targets at least 48px on touch layouts.

Apply these `DESIGN.md` component rules directly: square primary/secondary/tertiary/ghost buttons, tab-like timeline items with a 2px GSPE navy selected underline, feature cards with canvas background and hairline border, surface-1 bands for secondary regions, sentence-case labels, `letter-spacing: 0.16px` on body text, and no pill controls. The stage timeline is a product tab strip extended into a seven-step horizontal sequence. The layer manager uses flat bordered rows with an explicit switch state rather than rounded chips. Use no marketing-style gradients or glassmorphism in the page chrome.

## Product showcase information architecture

Treat the site as a product landing page first, with technical component pages as supporting product documentation. `showcase/index.html` is the GSPE APDU9953 landing page. It opens with a restrained GSPE product hero, product value statement, key ratings, a compact interactive 3D preview, and a clear route into component inspection. The hero presents the assembled product and one primary action such as “Explore the system”; it does not expose the full CAD control deck immediately. The horizontal seven-stage timeline remains available in the interactive preview and on the full inspection entry point.

Use a shared static shell so the site works from a file server or simple static host without a framework router:

- `showcase/index.html` — product landing page and overview viewer.
- `showcase/components/index.html` — component directory with seven module cards.
- `showcase/components/housing.html`
- `showcase/components/mounting.html`
- `showcase/components/power.html`
- `showcase/components/breakers.html`
- `showcase/components/outlet-banks.html`
- `showcase/components/nmc3.html`
- `showcase/components/internal-busbars-pcb.html`
- `showcase/assets/showcase.css` and `showcase/assets/showcase.js` — shared layout tokens, model-viewer behavior, stage state, layer visibility and accessible controls.

The seven module pages cover the selected user-facing layers. NMC3 receives an additional deep-detail page section within `nmc3.html`, with dedicated controller close-up framing, port family tabs (RJ45, USB-A, Micro-B), display/buttons, PCB and shielding tray, port-specific hotspot cards, and a focused exploded comparison. Do not create separate routes for every port or fastener.

Each module page uses one reusable product-detail template: breadcrumb back to APDU9953, component title and one-sentence role, a model-viewer panel with assembled/exploded and isolate controls, a concise specification block, a “how it fits” section linked to the landing timeline, and previous/next component navigation. Page-specific camera presets and hotspot metadata are declarative data, not duplicated control logic. Hidden-layer behavior follows the same explicit export contract as the landing viewer.

The component directory provides a flat grid of seven cards with GSPE module names, one-line purpose, visual status/material cue and a square “Open component” link. Landing page cards and directory cards link to the same canonical detail paths. Use `DESIGN.md`'s light canvas, surface-1 bands, hairlines, square cards and GSPE navy links; reserve dark surfaces for each 3D viewport only. Every detail page includes a compact “Back to product overview” path and preserves the GSPE brand system.

On narrow screens, the landing hero stacks product copy above the model preview, the component cards become one column, and detail page inspection controls move below the viewer. A persistent breadcrumb and visible page title preserve orientation. Browser history remains meaningful for page navigation; model mode and selected component state may use URL query parameters when useful but must degrade gracefully without JavaScript.

## Stages and state

The seven stages use the supplied titles and show a technical explanation, current stage indicator and appropriate camera target. Stage selection is the single source of truth for selected timeline item, assembled/exploded source, layer preset and camera transition. Camera presets adjust the view without changing the stage. Auto-rotation stops when a stage, preset or hotspot is selected.

1. Housing & Chassis Extrusion: housing inspection, front structural shell visible; mounting, power and electronics hidden.
2. Rear Dual-Pad Toolless Mounting: housing plus mounting, rear camera.
3. Power Whip & IEC 60309 Plug: cumulative structure/mounting/power, camera framed from actual exported cable/plug geometry.
4. Internal Relays, Busbars & PCB: assembled internals exposed by hiding occluding front housing/fascias; show structural shell, mounting, power and internal electronics. Separate front-cover geometry from the structural shell in export metadata to support this.
5. Front Controls, Rockers & Sockets: all components visible, camera focuses on the front controls.
6. Fully Assembled Unit: all components visible, full-unit framing.
7. 3D Exploded View: all components visible in the exploded source, framing covers the separated assembly.

Stage presets follow the existing cumulative story while the layer panel enables manual inspection. A manual layer change is visibly marked as a customized stage; selecting a stage again restores its preset. Switching assembled/exploded mode maps explicitly to stage 6/7. Retain the latest intended state during asset loading, including fast repeated stage selections, and apply visibility when the requested model loads.

## Layer and export contract

Expose exactly the seven user-facing controls: Chassis Housing, Mounting System, Power Whip Cord, Circuit Breakers, 24-Outlet Banks, NMC3 Controller, and Internal Busbars & PCB. A control affects its explicitly assigned geometry; internal contacts, relay boards, busbars and controller electronics belong to the internal layer. Breaker bodies remain in the breaker layer. Fasteners follow their retained component.

Extend the FreeCAD part metadata and mesh grouping with presentation roles only where required. Preserve existing subsystem identities in native CAD and add layer/role metadata for export. Give each exported layer/role/material combination a distinct material identity, retaining the PBR parameters. This permits the public model-viewer materials API to change visibility without affecting other layers or depending on private scene internals. Preserve original alpha/color values when showing geometry again.

Update `pdu_assembly.py`, the mesh exporter and Blender exporter as supporting files where needed; the current six groups/shared-material pipeline cannot implement the requested seven independent controls reliably. Clear or replace stale staging artifacts during rebuild so obsolete port meshes cannot enter the new GLBs.

## Coordinates and hotspots

Validate the actual FreeCAD-to-OBJ-to-Blender-to-glTF axis transform rather than assuming it. Export named hotspot coordinates/metadata from the pipeline and use consistent metre units in the viewer. Chassis locations derive from Z=0..1.829 m; cable and plug locations may lie above the chassis and must use their true exported positions.

Use one active tooltip card positioned from projected hotspot coordinates. Clamp the card inside the viewport's safe rectangle, choose the side with room, and place its triangle toward the anchor. Update on camera changes, resize and model switch; dismiss when its layer is hidden or its anchor is not visible. Separate tooltip content from the hotspot button to avoid nested interaction. Exploded coordinates include the appropriate component displacement.

## Verification and artifacts

Before geometry fixes, add targeted FreeCAD regression probes for text orientation and local port geometry. Verify valid solids, aperture/sample-point behavior, inversion, material separation and the asymmetric Micro-B profile. Audit text visually in rendered front close-ups. Build the requested STEP/FCStd, mesh staging and Blender assets in order, and inspect logs for exceptions or skipped meshes; command exit alone is insufficient.

Validate both GLB files structurally, including layer material identities, axis/height bounds, metadata and expected port parts. Use Playwright against a local server to check all seven stages, every layer independently, stage changes during loading, assembled/exploded switching, camera transitions, hotspot clamping and desktop/mobile layout. Inspect screenshots and browser errors.

Required outputs are the corrected FreeCAD source, rebuilt STEP/FCStd, rebuilt staging and Blender scenes, `showcase/gspe_pdu_apdu9953.glb`, `showcase/gspe_pdu_apdu9953_exploded.glb`, and redesigned `showcase/index.html`. Record verification results and any genuine limits. No deployment is requested.

## Review

The design contains no unresolved requirements or placeholders. Implementation awaits the user's review of this concrete design. This workspace currently has no Git repository, so the design is saved locally and cannot be committed here.
