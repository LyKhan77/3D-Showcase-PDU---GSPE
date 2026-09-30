# APDU9953 geometry refinement

All geometry uses millimetres: X across the face, Z upward, front along negative Y.
The assembly origin and existing vertical layout remain compatible with earlier files.

## Showcase: show/hide dan preset

Buka `openscad/pdu_apdu9953_assembly.scad`. Semua nilai awal `SHOW_*` adalah
`true`, `VIEW_STAGE="CUSTOM"`, dan `EXPLODE_FACTOR=0.0`.

| Flag manual | Bagian yang dikontrol |
| --- | --- |
| `SHOW_HOUSING` | Ekstrusi, end-caps, sekrup bodi, cover bank/breaker, plat branding/rating |
| `SHOW_MOUNTING` | Dua pasang pad, peg toolless, stud grounding, washer, nut dan simbol |
| `SHOW_POWER_ENTRY` | Gland, whip stub, plug IEC 60309, terminal block L/N/PE dan kabel pendek internal |
| `SHOW_FASCIA_EXTERNAL` | Bezel/face/shroud soket, indikator, rocker/guard, panel NMC3, LCD, tombol, port dan fastener panel |
| `SHOW_INTERNALS` | 72 kontak pegas, dua rel busbar kontinu, tiga PCB dengan 24 relay, mainboard/shield NMC3, bodi/lug breaker |
| `SHOW_FRONT_COVER` | Subgroup housing: dinding muka, cover bank/breaker dan plat label; `false` membuka channel depan |
| `SHOW_WHIP` | Subgroup power: gland, kabel luar dan plug; terminal block tetap terlihat |

Flag kelompok independen: mematikan housing tidak mematikan mounting atau elektronik.
Untuk membuka seluruh muka secara manual, set `SHOW_FRONT_COVER=false` dan
`SHOW_FASCIA_EXTERNAL=false`. Shroud isolator soket mengikuti kelompok external
agar kontak pegas tidak tertutup saat showcase internal.

Preset bersifat **kumulatif**, dan mengabaikan flag manual termasuk kedua subgroup:

| `VIEW_STAGE` | Housing | Mounting | Power | Internal | External | Cover depan | Explode |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `CUSTOM` | manual | manual | manual | manual | manual | manual | manual |
| `STAGE1_HOUSING` | ya | — | — | — | — | terbuka | 0 |
| `STAGE2_MOUNTING` | ya | ya | — | — | — | terbuka | 0 |
| `STAGE3_POWER` | ya | ya | ya | — | — | terbuka | 0 |
| `STAGE4_INTERNALS` | ya | ya | ya | ya | — | terbuka | 0 |
| `STAGE5_CONTROLS` | ya | ya | ya | ya | ya | tertutup | 0 |
| `STAGE6_COMPLETE` | ya | ya | ya | ya | ya | tertutup | 0 |
| `STAGE7_EXPLODED` | ya | ya | ya | ya | ya | terpasang terpisah | 0.6 |

Stage 5 dan 6 sengaja menghasilkan geometri rapat yang sama: stage 5 menjelaskan
kontrol, stage 6 menegaskan keadaan lengkap. Pilih kembali `CUSTOM` untuk
mengaktifkan nilai flag manual. Nama preset yang salah ditolak dengan assertion.
`EXPLODE_FACTOR` manual harus dalam [0, 1]; `1.0` berarti pemisahan maksimum.

Contoh dari root proyek:

```sh
rtk proxy openscad -D 'VIEW_STAGE="STAGE4_INTERNALS"' cad/apdu9953/openscad/pdu_apdu9953_assembly.scad
rtk proxy openscad -D 'SHOW_HOUSING=false' -D 'SHOW_MOUNTING=false' cad/apdu9953/openscad/pdu_apdu9953_assembly.scad
rtk proxy python3 cad/apdu9953/render_refinement.py mounting stage1 stage2 stage4 stage7
rtk proxy python3 cad/apdu9953/render_refinement.py grounding stage3 stage5 stage6
rtk proxy python3 cad/apdu9953/test_showcase.py
rtk proxy python3 cad/apdu9953/validate_refinement.py
```

Public assembly menerima parameter bernama `show_housing`, `show_mounting`,
`show_power_entry`, `show_fascia_external`, `show_internals`, `show_front_cover`,
`show_whip`, `view_stage`, dan `explode_factor`. Parameter tambahan ditambahkan
setelah parameter lama sehingga pemanggilan positional lama tetap kompatibel.
Flag diteruskan eksplisit ke submodule yang memiliki bagian tersebut:

- Chassis: `show_housing`, `show_front_cover`.
- Socket bank dan breaker: `show_housing`, `show_front_cover`, `show_fascia_external`, `show_internals`.
- Socket individual dan NMC3: `show_fascia_external`, `show_internals`.
- Power entry: `show_power_entry`, `show_whip`.
- Mounting: `show_mounting`, serta subgroup `show_pads`, `show_pegs`, `show_ground`.

Contoh mengisolasi peg dari file SCAD lain:

```openscad
use <modules/sub_mounting_pegs.scad>
sub_mounting_pegs(explode_factor=0.6, show_pads=false, show_ground=false);
```

Standalone submodule memakai default terlihat seluruhnya; preset hanya diselesaikan
di master assembly. Dua rail lokal per standalone bank dipertahankan untuk
kompatibilitas. Master menonaktifkannya melalui `show_busbars=false`, lalu memasang
**dua rel kontinu** sepanjang Z=219.5–1274.5 mm untuk seluruh tiga bank.

Render PNG memakai evaluasi penuh Manifold agar boolean dan kontak kecil tetap
terlihat tanpa artefak OpenCSG. Overview preset memakai `--viewall`, termasuk whip
500 mm dan plug. `WHIP_LEN=3000` tetap tersedia untuk panjang nominal.

## Component layers

Displacements below are millimetres multiplied by `explode_factor`, along Y relative
to each component's assembled location. X/Z remain aligned with their mounting locations.

| Part | Y displacement |
| --- | ---: |
| Chassis, cable gland/cord/plug | +200 |
| Main power terminal block | +110 |
| Mounting pads / pegs / pad locking screws | +235 / +285 / +253 |
| Ground stud / washer / nut | +225 / +233 / +241 |
| Rear end-cap screws | +220 |
| Fascias and branding plates | -12 |
| Breaker guard / rocker / screws | -24 / -43 / -65 |
| Breaker bakelite body / rear terminal lugs | +15 / +60 |
| Socket bezel / contact face / housing | -42 / -27 / +8 |
| Socket contact clips / neutral and PE busbars / relay PCB | +42 / +70 / +110 |
| Carrier plates, carrier screws, relay standoffs, busbar saddles | 0 (fixed to chassis) |
| Relay PCB screws | +110 (with the boards) |
| NMC display / glass relative to display / buttons / screws | -26 / -12 / -43 / -65 |
| NMC ports / PCB / shielding tray | +8 / +55 / +105 |
| NMC PCB screws | +55 (with the PCB) |
| NMC tray rear-wall screws | +105 (with the tray) |
| Breaker retainer plates and their screws | +15 (with the bodies) |
| Terminal block bracket, standoffs and screws | +110 (one cluster) |

Components are named submodules, so housing, bezel, clips, busbars, relay board, breaker
body/lugs, NMC connectors, display and PCB can also be instantiated independently.
Copper contacts total 72 (three per outlet); relay modules total 24 (eight per bank).

## Reference decisions and limits

Inspected references:

- `temp/ss/Screenshot 2026-09-29 at 12.01.00.png`: guard wings, curved stepped rocker, lower rating, fasteners.
- `temp/ss/Screenshot 2026-09-29 at 12.03.49.png`: top C15 key with round relief, three vertical apertures,
  recessed moat, centered white LED and adjacent optical pinhole, left numbering/guide.
- `references/images/sketchfab_ns9000/annotation_1.png`: NMC port arrangement, display/menu, buttons and labels.
- `specs/apdu9953_ns9000_switched.yaml`: chassis envelope, pitch, outlet count, bank layout and branding.

The task and socket photograph override the older YAML description of a bottom C15 notch
and a green 2.5 mm LED: the revised model uses the top key and a white 2.2 mm dome.
The chassis retains its powder-coated appearance. YAML describes steel while the task calls
it aluminium; geometric rendering cannot establish the physical alloy.

The 1829 x 56 x 46 mm chassis envelope and 28.5 mm socket pitch are preserved.
Socket bezel corner radius is 1.8 mm. Breaker depth is 35 mm internally; its guard projects
12 mm ahead of the chassis. GSPE colors use #003674 and #FAFFD8.

Internal construction, PCB component packages/placement, spring contacts, lug details and
T15 recesses are visual reconstructions. Photographs provide no calibrated dimensions for
these details. This is an exploded-view CAD visualization, not a certified 1:1 manufacturer
model, production drawing, electrical schematic or validated connector mating design.

## Validation

`validate_refinement.py` compiles all 11 SCAD sources at factors 0, 0.6 and 1 using
`--hardwarnings`. It exports nine public component/assembly models at all three factors
with the Manifold backend, then independently checks binary STL edge incidence, winding,
duplicate-vertex degeneracy and positive signed volume. The 60 original checks are retained. Seven presets and five isolated manual groups
are additionally compiled and exported: **84 checks total**. Isolated groups use
factor 0.6; the preset itself determines its effective factor.
`test_showcase.py` independently verifies an empty scene with all groups off,
geometry changes for each flag, all seven preset overrides (including conflicting
manual flags/explosion), and rejection of unknown stage names.

A 0.04 mm gap between the socket face and recessed floor prevents coincident mating
edges from collapsing when serialized to STL. Metal connector shells and curved rocker
silkscreen use explicit CSG evaluation to avoid OpenCSG preview artifacts.

Results and per-command logs: `temp/apdu9953_validation/validation_report.json`.
Render commands: `temp/apdu9953_validation/render_manifest.json`.
Original SCAD backup: `temp/apdu9953_before_refinement/`.

Watertight mesh checks do not prove electrical clearance, manufacturability, exact reference
agreement, or collision-free disassembly throughout every intermediate factor.

## LAN correction after direct Sketchfab inspection (2026-09-29)

Inspected `temp/ss/Screenshot 2026-09-29 at 13.53.11.png` and navigated the live
[Schneider Electric Sketchfab model](https://sketchfab.com/3d-models/apc-netshelter-9000-series-rack-pdu-706fa965c59f43ee8eea7a08ec8b147b),
including its Enhanced Management Card annotation and an enlarged oblique port view.
Live capture: `output/playwright/sketchfab-lan-live-zoom.png`.

The previous generic RJ45 had a silver collar, a bottom latch and top contacts on
all four ports. The reference uses a tall dark housing with a substantial lower
skirt for Link A, Link B and Network, eight contacts on the cavity floor, a top
latch and two white light-pipe lenses. Universal I/O has the opposite orientation
and no corner light pipes. These differences are now separate module parameters.

The revised RJ45 uses a 20 x 22.4 mm visual housing envelope, front bevel, thin
folded shielding, recessed stepped cavity and side bearing ledges. Port centers
are X = ±12 mm and Z = 10, -18, -46 mm within the controller. The panel openings
and printed port labels follow the same layout. Network's green/amber emitters
remain behind neutral lenses, with two circular indicators and the 1000/100/10
legend above the jack. Contact appearance uses the pale green tint visible in the
reference viewer; this is a rendering choice, not a claim about the actual plating.

Additional close-up: `previews/apdu9953_close_lan_revised.png`.
Backup before this correction: `temp/apdu9953_before_lan_refinement/`.
Housing dimensions are inferred visual proportions, not calibrated manufacturer dimensions.

## Mechanical fastening completion (2026-09-29)

A full mounting audit was performed and every component now has an explicit
retention path. Backup before this task: `temp/apdu9953_before_mounting_audit/`.

### Single source of truth

All mounting coordinates live in `openscad/modules/detail_common.scad`
(`LAYOUT_*` vertical positions plus one function per fastener pattern:
`bank_carrier_pts`, `bank_relay_pts`, `brk_retainer_pts`, `nmc_tray_pts`,
`nmc_pcb_pts`, `fascia_side_z`, `terminal_bracket_pts`). The chassis drills its
clearance/counterbore holes from the same functions that place the bosses,
standoffs and screws, so a hole and its fastener can never drift apart. The
master assembly aliases `BANK*/BRK*/NMC_Z` from the same `LAYOUT_*` constants.
Finding confirmed and fixed: the NMC tray bosses used to sit at ±22/±97 while
the main PCB holes are at ±21/±96; both now consume `nmc_pcb_pts` and the
bosses are real standoffs bridging the tray rear wall to the PCB.

### Mounting registry (design reconstruction, not manufacturer data)

| Komponen | Metode | Dudukan induk | Titik (sumber) | Pengikat | Arah lepas |
| --- | --- | --- | --- | --- | --- |
| Chassis ke rack | toolless peg + pad | dinding belakang chassis | pitch 1680, Z 74.5/1754.5 | peg central Torx T15 drive | sumbu Y |
| Fascia bank (×3) | wrap-flange + sekrup samping | insert kuningan dinding samping | `fascia_side_z` (±100), Y −20 | 4× Torx csk M3/sisi… 4 total per fascia | sumbu X |
| Faceplate NMC | wrap-flange + sekrup samping | insert kuningan dinding samping | `fascia_side_z` (±100) | 4× Torx csk M3 | sumbu X |
| Housing soket (×24) | snap-fit latch | slot fascia per outlet | tepi ±(h/2+1.25) latch | tanpa baut (2 cantilever) | −Y saat fascia terbuka |
| Plat carrier bank (×3) | 4 sekrup belakang | dinding belakang chassis | `bank_carrier_pts` (±19, ±110) | 4× Torx csk M3, ulir di plat 2 mm | sumbu Y |
| PCB relay (×3) | 4 standoff berulir | plat carrier | `bank_relay_pts` (±20, ±113) = lubang PCB | 4× Torx M2.5 dari muka PCB | sumbu Y |
| Rel busbar kontinu (×2) | saddle isolator nilon | lengan ke plat carrier | X ±24, Z tengah tiap bank | 1× Torx M3 per saddle (6 total) | sumbu Y |
| Bodi breaker (×2) | plat retainer belakang | dinding belakang chassis | `brk_retainer_pts` (−7, ±14) | 2× Torx csk M3 | sumbu Y |
| Lug breaker (×4) | clamp screw vertikal | bodi breaker | poros (−7, ±10) | 1× Torx M2.5 vertikal per lug | sumbu Z |
| Tray shielding NMC | 4 sekrup belakang | dinding belakang chassis | `nmc_tray_pts` (±21, ±101) | 4× Torx csk M3 | sumbu Y |
| Main PCB NMC | 4 standoff tray | dinding belakang tray | `nmc_pcb_pts` (±21, ±96) = lubang PCB | 4× Torx M2.5 dari muka PCB | sumbu Y |
| Terminal block L/N/PE | bracket + 4 standoff | top cap | `terminal_bracket_pts` (±14, ±9) | 4× Torx csk M3 vertikal | sumbu Z |
| Kabel internal whip | saddle clamp | 2 post ke bracket | X ±13, 0 | tanpa baut (klamp) | — |
| Grounding M5 | stud + washer + nut | dinding belakang chassis | X 10, Z 150 | mur hex 8 mm AF | sumbu Y |

Sekrup samping terlihat di dekat casing controller pada referensi
(`output/playwright/sketchfab-side-fasteners.png`); fungsi sambungan internalnya
tidak terkonfirmasi, jadi dipakai sebagai sekrup flange fascia yang masuk ke
insert dinding samping — keputusan desain sendiri, bukan klaim 1:1 terhadap
produk Schneider.

### Exploded-view displacements for the new hardware

Carrier plates, carrier screws, relay standoffs and busbar saddles stay at 0
(they are the fixed chassis-attached spine). Relay PCBs and their screws +110,
busbars +70, the NMC tray with its screws and standoffs +105, the NMC PCB and
its screws +55, fascias with side screws −12, breaker bodies with retainer
plates and screws +15 (lugs +60), and the terminal block moves with its
bracket, standoffs and screws as one cluster +110. At `explode_factor=0` every
pattern re-seats exactly (probed, see below).

### Show/hide semantics for fasteners

No separate `SHOW_FASTENERS` flag was added: every fastener, bracket and
standoff follows its parent component group (fascia screws with the fascia
cover subgroup, carrier hardware with `SHOW_INTERNALS`, the terminal bracket
with `SHOW_POWER_ENTRY`, inserts with `SHOW_HOUSING`), so hiding a group never
orphans its hardware. The side-wall inserts belong to the chassis and remain
visible whenever housing is shown.

### Validation

`validate_refinement.py` now also runs `audit_mounting.py` (66 checks):
pattern-function parsing and alignment, single-source usage checks, a
clearance budget, ten rendered intersection probes that must be empty at
explode 0 (e.g. relay board vs carrier screws, retainer plate vs lugs, peg vs
pad bore), two positive controls that must intersect, five assembly-level
visibility probes (hidden groups leave no stray hardware), and explode-sign
checks per group. Full suite: 84/84 mesh checks + 66/66 mounting audit.
Reports: `temp/apdu9953_validation/mounting_audit_report.json`.

### Assumptions (not verified against the real product)

Carrier plate 2 mm with tapped M3 holes; 4.6 mm relay standoffs; M2.5 PCB
screws; nylon busbar saddles at bank centres only; breaker retainer as a
stamped plate; NMC tray screwed through the rear wall; terminal bracket hung
from the top cap; brass side-wall press inserts; snap-fit socket latches;
locking set-screw on the toolless peg. All are plausible reconstructions for a
visualization model — not certified construction.

## Rear mounting refinement (2026-09-29)

Inspected both `references/images/sketchfab_ns9000/annotation_8.png` and
`references/images/sketchfab_ns9000/05_embed_rear.png`. The annotation establishes
separate upper peg pad / lower locator pad and two fasteners at the rear top edge.
The rear overview is too small to calibrate the grounding position precisely.

Each peg station now uses two 42 x 42 x 6 mm pads, R2.5 footprint and 0.9 mm bevel.
Pad centers are separated by 52 mm vertically (10 mm edge gap); the secondary pad
sits directly below the primary. Primary pads have a Ø6.4 through bore, Ø16.4 flange
seat and a separate Torx locking screw. Peg center pitch remains **1680 mm**, at
Z=74.5 and 1754.5 mm; the lowest locator edge remains within the chassis at Z=1.5.
The task's square-pad requirement takes precedence over apparent rectangular
proportions in the uncalibrated screenshot.

The stainless peg contains a Ø16 x 2.5 flange, Ø6 x 17.5 neck, Ø12 x 5 mushroom
head with bevels on both edges, a recessed six-lobe Torx drive and an embedded anchor.
The peg moves 50 mm times `explode_factor` farther rearward than its pad, exposing
the bore. Pad locking screws also separate. Rear-facing countersunk Torx fasteners
sit at X=±19, Z=1822 on the upper end-cap return. The lower rear grounding assembly
at X=10, Z=150 has an M5 brass stud with visual thread rings, Ø12 washer, 8 mm AF hex
nut, and raised grounding symbol beside it. Washer and nut separate in exploded view.

These detail dimensions and grounding position are explicit reconstruction choices,
not manufacturer measurements. Envelope and peg pitch retain their specified values;
photo-based detailing does not establish certified 1:1 fidelity.

Delivered PNGs in `previews/`:

- `apdu9953_close_mounting_dualpad.png`
- `apdu9953_stage1_housing.png`
- `apdu9953_stage2_mounting.png`
- `apdu9953_stage4_internals.png`
- `apdu9953_stage7_exploded.png`

Mounting-audit set (2026-09-29): `apdu9953_side_fasteners.png`,
`apdu9953_internal_mounting.png`, `apdu9953_controller_mounting.png`,
`apdu9953_internal_mounting_exploded.png`.

Additional verification views: `apdu9953_close_grounding.png`,
`apdu9953_stage3_power.png`, `apdu9953_stage5_controls.png`,
`apdu9953_stage6_complete.png`.
Backup before this task: `temp/apdu9953_before_showcase/`.
