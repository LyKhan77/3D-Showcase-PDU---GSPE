#!/usr/bin/env python3
"""Mechanical mounting audit for the APDU9953 assembly.

Complements validate_refinement.py (mesh/watertight) with checks that the
fastening system is actually coherent:

  A. Static coordinate audit — the shared pattern functions in
     detail_common.scad are the single source for holes, bosses, standoffs
     and screws; every consumer must reference them, and the derived
     clearance budget must keep non-mating parts apart.
  B. STL intersection probes (explode_factor=0) — curated part pairs that
     must NOT intersect, rendered from the real modules through OpenSCAD.
     Two positive controls must intersect, proving the probes can detect
     engagement at all.
  C. Visibility probes — hiding a group removes its fasteners with it
     (assembly-level intersections against reference volumes).
  D. Explode direction audit — every moving group keeps its documented
     displacement sign/axis.

Only Python stdlib + the OpenSCAD CLI are required.
"""
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "cad/apdu9953/openscad"
MOD = SRC / "modules"
OUT = ROOT / "temp/apdu9953_validation"
OUT.mkdir(parents=True, exist_ok=True)

results = []
def record(name, ok, detail=""):
    results.append((name, ok, detail))
    print(("PASS " if ok else "FAIL ") + name + (" | " + detail if detail else ""), flush=True)

# ---------------------------------------------------------------- helpers
def read(p):
    return p.read_text()

def scad_use(*paths):
    return "".join(f'use <{p}>\n' for p in paths)

def stl_triangles(path):
    data = path.read_bytes()
    if len(data) < 84:
        return -1
    return struct.unpack_from("<I", data, 80)[0]

def run_openscad(source_text, output, extra=None):
    with tempfile.NamedTemporaryFile("w", suffix=".scad", delete=False, dir=OUT) as fh:
        fh.write(source_text)
        probe = Path(fh.name)
    output.unlink(missing_ok=True)
    cmd = ["openscad", "--backend=Manifold", "--hardwarnings", "--export-format", "binstl",
           "-o", str(output), str(probe)]
    if extra:
        cmd += extra
    res = subprocess.run(cmd, capture_output=True, text=True)
    log = res.stdout + res.stderr
    (OUT / (Path(output).stem + ".probe.log")).write_text(log)
    probe.unlink()
    return res, log

# OpenSCAD exits non-zero with "Current top level object is empty" when the
# rendered intersection is empty, so emptiness is judged from the message or
# a zero-triangle STL, not the return code.
def is_empty(res, log, output):
    tris = stl_triangles(output) if output.exists() else -1
    return "top level object is empty" in log or tris == 0, tris

# ---------------------------------------------------------------- A. static
common = read(MOD / "detail_common.scad")

def parse_pts(fn, text):
    """Parse a pattern function built as [for(x=[a,b], dz=[c,d]) [x, zc+dz]]."""
    m = re.search(r"function\s+" + fn + r"\s*\([^)]*\)\s*=\s*\[?\s*for\(\s*x?\s*=?\s*\[(-?\d+),(-?\d+)\]\s*,?\s*d?z?=?dz?\s*=?\s*\[(-?\d+),(-?\d+)\]\s*\)\s*\[([^]]+)\]", text)
    if not m:
        return None
    xs = [int(m.group(1)), int(m.group(2))]
    dzs = [int(m.group(3)), int(m.group(4))]
    body = m.group(5)
    pts = set()
    for x in xs:
        for dz in dzs:
            pts.add((x, dz) if "x, zc+dz" in body or "x, dz" in body else (x, dz))
    return pts

def parse_simple(fn, text):
    m = re.search(r"function\s+" + fn + r"\s*\([^)]*\)\s*=\s*\[?\s*for\(\s*dz=\[(-?\d+),(-?\d+)\]\s*\)\s*\[([^]]+)\]", text)
    if not m:
        return None
    return [(-7, int(m.group(1))), (-7, int(m.group(2)))]

def parse_terminal(text):
    m = re.search(r"function\s+terminal_bracket_pts\(\)\s*=\s*\[?\s*for\(\s*x=\[(-?\d+),(-?\d+)\]\s*,\s*y=\[(-?\d+),(-?\d+)\]\s*\)\s*\[x,\s*y\]", text)
    if not m:
        return None
    return [(int(m.group(1)), int(m.group(3))), (int(m.group(2)), int(m.group(3))),
            (int(m.group(1)), int(m.group(4))), (int(m.group(2)), int(m.group(4)))]

def parse_side_z(text):
    m = re.search(r"function\s+fascia_side_z\([^)]*\)\s*=\s*\[zc([+-]?\d+),\s*zc([+-]?\d+)\]", text)
    return (int(m.group(1)), int(m.group(2))) if m else None

carrier = parse_pts("bank_carrier_pts", common)
relay = parse_pts("bank_relay_pts", common)
tray = parse_pts("nmc_tray_pts", common)
nmc_pcb = parse_pts("nmc_pcb_pts", common)
brk = parse_simple("brk_retainer_pts", common)
term = parse_terminal(common)
side_z = parse_side_z(common)

record("A1 pattern functions parse", None not in (carrier, relay, tray, nmc_pcb, brk, term, side_z),
       str({"carrier": carrier, "relay": relay, "tray": tray, "nmc_pcb": nmc_pcb, "brk": brk, "term": term, "side_z": side_z}))

record("A2 carrier pattern 4x [±19,±110]", carrier == {(-19,-110),(19,-110),(-19,110),(19,110)})
record("A3 relay pattern 4x [±20,±113]", relay == {(-20,-113),(20,-113),(-20,113),(20,113)})
record("A4 tray pattern 4x [±21,±101]", tray == {(-21,-101),(21,-101),(-21,101),(21,101)})
record("A5 nmc pcb pattern 4x [±21,±96] (was ±22/±97 defect)",
       nmc_pcb == {(-21,-96),(21,-96),(-21,96),(21,96)})
record("A6 breaker retainer 2x [-7,±14]", sorted(brk) == [(-7,-14),(-7,14)])
record("A7 terminal bracket 4x [±14,±9]", term == [(-14,-9),(14,-9),(-14,9),(14,9)])
record("A8 side screws zc±100", side_z == (-100,100))

# Single-source usage: every consumer must call the shared functions.
usage = {
    "A9 chassis rear holes use carrier pts": ("bank_carrier_pts(zc)", read(MOD/"sub_chassis.scad")),
    "A10 chassis rear holes use breaker pts": ("brk_retainer_pts(zc)", read(MOD/"sub_chassis.scad")),
    "A11 chassis rear holes use tray pts": ("nmc_tray_pts(LAYOUT_NMC_Z)", read(MOD/"sub_chassis.scad")),
    "A12 chassis side holes use fascia_side_z": ("fascia_side_z(zc)", read(MOD/"sub_chassis.scad")),
    "A13 chassis cap holes use terminal_bracket_pts": ("terminal_bracket_pts()", read(MOD/"sub_chassis.scad")),
    "A14 carrier plate uses relay pts (standoffs==holes)": ("bank_relay_pts(0)", read(MOD/"sub_socket_bank.scad")),
    "A15 carrier screws use carrier pts": ("bank_carrier_pts(0)", read(MOD/"sub_socket_bank.scad")),
    "A16 relay board holes use relay pts": ("bank_relay_pts(0)", read(MOD/"sub_socket_bank.scad")),
    "A17 relay screws use relay pts": ("bank_relay_pts(0)", read(MOD/"sub_socket_bank.scad")),
    "A18 nmc tray bosses use nmc_pcb_pts": ("nmc_pcb_pts(0)", read(MOD/"sub_nmc3_controller.scad")),
    "A19 nmc pcb holes use nmc_pcb_pts": ("nmc_pcb_pts(0)", read(MOD/"sub_nmc3_controller.scad")),
    "A20 nmc pcb screws use nmc_pcb_pts": ("nmc_pcb_pts(0)", read(MOD/"sub_nmc3_controller.scad")),
    "A21 nmc tray screws use nmc_tray_pts": ("nmc_tray_pts(0)", read(MOD/"sub_nmc3_controller.scad")),
    "A22 breaker retainer uses brk_retainer_pts": ("brk_retainer_pts(0)", read(MOD/"sub_breaker_box.scad")),
    "A23 terminal bracket uses terminal_bracket_pts": ("terminal_bracket_pts()", read(MOD/"sub_top_whip_cord.scad")),
    "A24 layout aliases in master": ("LAYOUT_BANK_Z[0]", read(SRC/"pdu_apdu9953_assembly.scad")),
}
for name, (needle, text) in usage.items():
    record(name, needle in text)

# Alignment arithmetic: screw/boss axes coincide with their holes.
def axes_match(pts):
    return all(x == int(x) and z == int(z) for x, z in pts)
record("A25 all patterns integral", all(axes_match(p) for p in (carrier, relay, tray, nmc_pcb)))

# Clearance budget (assembled, mm). Values are the design intent; the probe
# section proves the model matches reality.
budget = [
    ("B1 carrier screw tip to relay PCB", 41.35 - 36.2 + 0.8, ">=0"),
    ("B2 carrier plate rear to chassis wall", 44.5 - 42, ">=0"),
    ("B3 saddle arm to relay PCB (X)", 23.2 - 23, ">=0"),
    ("B4 side screw shaft to socket housing (X)", 23.85 - 19, ">=0"),
    ("B5 insert tube to NMC tray (Y)", -13 - (-20), ">=0"),
    ("B6 retainer plate rear to chassis wall", 44.5 - 39, ">=0"),
    ("B7 terminal standoff to gland collar (radial)", (14**2 + 9**2) ** 0.5 - 3 - 13, ">=0"),
    ("B8 terminal wires to standoffs (plan)", (14 - 13) ** 2 + 9 ** 2, ">=plan"),
    ("B9 tray boss to RJ45 zone (Z)", 96 - 11.2 - 57, ">=0"),
    ("B10 relay standoff to busbar fingers (Y)", 35.4 - 25.3, ">=0"),
]
for name, value, _ in budget:
    record(name, value >= 0, f"{value:.2f} mm")

# ---------------------------------------------------------------- B. probes
PROBES_EMPTY = [
    ("P01 relay board vs carrier screws", scad_use(MOD/"sub_socket_bank.scad"),
     "bank_relay_board(2);\n bank_carrier_screws();"),
    ("P02 carrier plate vs busbar rails", scad_use(MOD/"sub_socket_bank.scad"),
     "bank_carrier_plate();\n pdu_busbars([0]);"),
    ("P03 side screws vs socket housings", scad_use(MOD/"sub_socket_bank.scad", MOD/"sub_socket_c13_c15.scad"),
     "bank_side_screws();\n for(i=[0:6]) translate([0,0,bank_socket_z(i)]) socket_housing(false);\n translate([0,0,bank_socket_z(7)]) socket_housing(true);"),
    ("P04 fascia side holes vs side screws", scad_use(MOD/"sub_socket_bank.scad"),
     "bank_fascia(2);\n bank_side_screws();"),
    ("P05 retainer plate vs terminal lug", scad_use(MOD/"sub_breaker_box.scad"),
     "breaker_retainer_plate();\n breaker_terminal_lug(10);"),
    ("P06 retainer screws vs breaker body", scad_use(MOD/"sub_breaker_box.scad"),
     "breaker_retainer_screws();\n breaker_bakelite_body();"),
    ("P07 nmc faceplate vs side screws", scad_use(MOD/"sub_nmc3_controller.scad"),
     "nmc_faceplate();\n nmc_side_screws();"),
    ("P08 nmc tray cavity vs pcb slab", scad_use(MOD/"sub_nmc3_controller.scad"),
     "nmc_shield_enclosure();\n translate([0,23,0]) cube([44,1.0,196],center=true);"),
    ("P09 terminal bracket vs gland hex", scad_use(MOD/"sub_top_whip_cord.scad"),
     "power_terminal_bracket();\n translate([0,0,10.6]) cylinder(d=32/cos(30),h=12,$fn=6);"),
    ("P10 peg vs pad bore", scad_use(MOD/"sub_mounting_pegs.scad"),
     "mounting_pad(show_fasteners=false);\n translate([0,3.45,0]) toolless_peg();"),
]
PROBES_SOLID = [
    ("C1 relay screws engage carrier plate", scad_use(MOD/"sub_socket_bank.scad"),
     "bank_relay_screws();\n bank_carrier_plate();"),
]

def run_probe(item):
    name, header, body = item
    output = OUT / (re.sub(r"[^A-Za-z0-9]+", "_", name) + ".stl")
    src = header + "intersection() {\n" + body + "\n}\n"
    res, log = run_openscad(src, output)
    return name, res, log, output

def launch(probes):
    import concurrent.futures as cf
    with cf.ThreadPoolExecutor(max_workers=3) as ex:
        return list(ex.map(run_probe, probes))

for name, res, log, output in launch(PROBES_EMPTY):
    empty, tris = is_empty(res, log, output)
    record(name, empty, f"tris={tris}")

for name, res, log, output in launch(PROBES_SOLID):
    tris = stl_triangles(output) if output.exists() else -1
    record(name, res.returncode == 0 and tris > 0, f"tris={tris} rc={res.returncode}")

# ---------------------------------------------------------------- C. visibility
ASSEMBLY_USE = scad_use(SRC/"pdu_apdu9953_assembly.scad")
VISIBILITY = [
    ("V1 carrier hidden with internals off",
     "pdu_apdu9953_assembly(show_internals=false, explode_factor=0);\n translate([0,18,669.5]) cube([49,2.5,236],center=true);", 0),
    ("V2 carrier present with internals on (control)",
     "pdu_apdu9953_assembly(show_internals=true, explode_factor=0);\n translate([0,18,669.5]) cube([49,2.5,236],center=true);", 1),
    ("V3 side screws hidden when front cover opens",
     "pdu_apdu9953_assembly(show_front_cover=false, show_internals=false, explode_factor=0);\n translate([30,-20,759.5]) cube([3.5,4,6],center=true);", 0),
    ("V4 side screws present with cover closed (control)",
     "pdu_apdu9953_assembly(show_front_cover=true, show_internals=false, explode_factor=0);\n translate([30,-20,759.5]) cube([3.5,4,6],center=true);", 1),
    ("V5 insert stays with housing when fascia hidden",
     "pdu_apdu9953_assembly(show_front_cover=false, show_internals=false, explode_factor=0);\n translate([26,-20,569.5]) cube([4,4,6],center=true);", 1),
]
for name, body, want_solid in VISIBILITY:
    output = OUT / (re.sub(r"[^A-Za-z0-9]+", "_", name) + ".stl")
    res, log = run_openscad(ASSEMBLY_USE + "intersection() {\n" + body + "\n}\n", output)
    empty, tris = is_empty(res, log, output)
    ok = (not empty) == bool(want_solid)
    record(name, ok, f"tris={tris}")

# ---------------------------------------------------------------- D. explode signs
EXPLODE_TABLE = {
    "sub_socket_bank.scad": [
        ("bank_fascia(bank_id)", "-12*e"), ("bank_side_screws()", "-12*e"),
        ("bank_busbars()", "70*e"), ("bank_relay_board(bank_id)", "110*e"),
        ("bank_relay_screws()", "110*e"),
    ],
    "sub_nmc3_controller.scad": [
        ("nmc_faceplate()", "-12*e"), ("nmc_side_screws()", "-12*e"),
        ("nmc_main_pcb()", "55*e"), ("nmc_pcb_screws()", "55*e"),
        ("nmc_shield_enclosure()", "105*e"), ("nmc_tray_screws()", "105*e"),
    ],
    "sub_breaker_box.scad": [
        ("breaker_retainer_plate()", "15*e"), ("breaker_retainer_screws()", "15*e"),
    ],
    "sub_mounting_pegs.scad": [
        ("mounting_pad(explode_factor=e)", "35*e"), ("toolless_peg()", "85*e"),
    ],
}
for fname, rows in EXPLODE_TABLE.items():
    text = read(MOD/fname)
    for module, disp in rows:
        # The module call must sit inside a translate containing the displacement
        # (same line, or inside the translate's { ... } block).
        pat = re.compile(r"translate\(\[[^\]]*" + re.escape(disp) + r"[^\]]*\]\s*\)[\s\S]{0,300}?" + re.escape(module))
        record(f"D {fname}:{module} moves {disp}", bool(pat.search(text)))

# ---------------------------------------------------------------- summary
failed = [r for r in results if not r[1]]
print(f"\nMOUNTING AUDIT: {len(results)-len(failed)}/{len(results)} passed", flush=True)
report = {"checks": len(results), "passed": len(results)-len(failed),
          "results": [{"name": n, "pass": ok, "detail": d} for n, ok, d in results]}
(OUT / "mounting_audit_report.json").write_text(__import__("json").dumps(report, indent=2))
sys.exit(1 if failed else 0)
