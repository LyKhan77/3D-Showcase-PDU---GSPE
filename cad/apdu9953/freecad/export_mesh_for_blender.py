# =====================================================================
# export_mesh_for_blender.py — Ekspor Mesh Terstruktur Hierarkis untuk Blender
# APDU9953 NetShelter 9000 Switched Rack PDU
# Men-tessellasi solid B-Rep FreeCAD via OpenCASCADE menjadi mesh OBJ
# terstruktur per (sub-sistem, material) untuk Assembled & Exploded view.
# =====================================================================
import os
import sys
import time
import json
import shutil

CAD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CAD_DIR)))
if CAD_DIR not in sys.path:
    sys.path.insert(0, CAD_DIR)

import FreeCAD as App
import Mesh
import MeshPart
from pdu_assembly import collect_parts
from modules._common import (
    GSPE_NAVY, GSPE_CREAM, CHASSIS_DARK, POLY_DARK, METAL_STEEL,
    COPPER, BRASS_GOLD, PCB_GREEN, LCD_SCREEN, PLUG_BLUE, LED_WHITE,
    LED_GREEN, LED_AMBER, LED_RED, BAKELITE_BLK, NYLON_WHITE, FPC_AMBER
)

STAGING_BASE = os.path.join(ROOT_DIR, "temp", "blender_staging_apdu9953")
LAYER_LABELS = {
    "housing": "Chassis Housing", "mounting": "Mounting System", "power": "Power Whip Cord",
    "breakers": "Circuit Breakers", "outlet_banks": "24-Outlet Banks", "nmc3": "NMC3 Controller",
    "internal": "Internal Busbars & PCB",
}

MAT_MAPPING = {
    "mat_chassis_powdercoat": [CHASSIS_DARK, (0.078, 0.090, 0.118), (0.118, 0.133, 0.176), (0.071, 0.102, 0.133)],
    "mat_gspe_navy":          [GSPE_NAVY],
    "mat_gspe_cream":         [GSPE_CREAM, (0.957, 0.957, 0.949)],
    "mat_polyamide_dark":     [POLY_DARK, BAKELITE_BLK, (0.255, 0.271, 0.290), (0.114, 0.133, 0.165), (0.161, 0.176, 0.196), (0.216, 0.231, 0.251), (0.125, 0.145, 0.173), (0.153, 0.173, 0.192), (0.141, 0.161, 0.188), (0.145, 0.176, 0.208), (0.271, 0.302, 0.341)],
    "mat_steel_metal":        [METAL_STEEL, (0.290, 0.318, 0.345), (0.227, 0.255, 0.286), (0.733, 0.757, 0.776)],
    "mat_glass_clear":        [(0.700, 0.850, 0.900)],
    "mat_copper_busbars":     [COPPER],
    "mat_brass_gold":         [BRASS_GOLD],
    "mat_pcb_green":          [PCB_GREEN],
    "mat_lcd_screen":         [LCD_SCREEN],
    "mat_plug_blue":          [PLUG_BLUE, (0.100, 0.350, 0.580)],
    "mat_led_white":          [LED_WHITE],
    "mat_led_green":          [LED_GREEN, (0.000, 0.812, 0.412), (0.659, 0.875, 0.294)],
    "mat_led_amber":          [LED_AMBER, (0.894, 0.675, 0.298)],
    "mat_led_red":            [LED_RED],
    "mat_nylon_white":        [NYLON_WHITE],
    "mat_fpc_amber":          [FPC_AMBER],
    "mat_cap_blue":           [(0.141, 0.247, 0.404), (0.137, 0.263, 0.416), (0.129, 0.467, 0.675)],
    "mat_wire_brown":         [(0.463, 0.325, 0.227)],
    "mat_wire_green":         [(0.365, 0.580, 0.220)],
    "mat_rubber_black":       [(0.045, 0.050, 0.058)],
}

# Preserve established assignments for source colours that overlap multiple
# presentation palettes. All other colours use nearest registered colour.
LEGACY_ASSIGNMENTS = {
    (0.080, 0.085, 0.095): "mat_chassis_powdercoat",
    (0.114, 0.133, 0.165): "mat_chassis_powdercoat",
    (0.125, 0.145, 0.173): "mat_chassis_powdercoat",
    (0.133, 0.153, 0.176): "mat_chassis_powdercoat",
    (0.141, 0.161, 0.188): "mat_chassis_powdercoat",
    (0.133, 0.169, 0.161): "mat_polyamide_dark",
    (0.290, 0.318, 0.345): "mat_polyamide_dark",
    (0.227, 0.255, 0.286): "mat_polyamide_dark",
    (0.950, 0.950, 0.950): "mat_gspe_cream",
}

def find_mat_name(color):
    for source, mat_name in LEGACY_ASSIGNMENTS.items():
        if all(abs(a - b) <= 1e-9 for a, b in zip(color, source)):
            return mat_name
    best_name = None
    best_distance = float("inf")
    for mat_name, colors in MAT_MAPPING.items():
        for registered in colors:
            distance = max(abs(a - b) for a, b in zip(color, registered))
            if distance <= 0.03 and distance < best_distance:
                best_name = mat_name
                best_distance = distance
    if best_name is not None:
        return best_name
    print(f"Warning: unmatched material color {tuple(round(c, 6) for c in color)}; defaulting to mat_steel_metal")
    return "mat_steel_metal"

def export_state(mode_name, explode=0.0):
    t0 = time.time()
    out_dir = os.path.join(STAGING_BASE, mode_name)
    os.makedirs(out_dir, exist_ok=True)
    print(f"\n--- Exporting {mode_name.upper()} State (explode={explode}) ---")

    doc = App.newDocument(f"Doc_{mode_name}")
    App.setActiveDocument(doc.Name)
    parts = collect_parts(doc=doc, stage="CUSTOM", explode=explode)
    print(f"Total komponen solid: {len(parts)}")

    # Kelompokkan parts per (presentation layer, role, material)
    grouped = {}
    manifest_parts = []
    for p in parts:
        layer = p.get("layer")
        role = p.get("role")
        if not layer or not role:
            raise ValueError(f"Part {p['name']} has no presentation layer/role")
        mname = find_mat_name(p["color"])
        key = f"{layer}__{role}__{mname}"
        grouped.setdefault(key, []).append(p)
        bb = p["shape"].BoundBox
        manifest_parts.append({
            "name": p["name"], "layer": layer, "role": role, "material": mname,
            "bounds_mm": [bb.XMin, bb.YMin, bb.ZMin, bb.XMax, bb.YMax, bb.ZMax],
        })

    for key, gparts in grouped.items():
        sub_meshes = []
        for p in gparts:
            try:
                m = MeshPart.meshFromShape(p["shape"], LinearDeflection=0.1, AngularDeflection=0.2)
                if m.CountFacets > 0:
                    sub_meshes.append(m)
            except Exception as err:
                print(f"Warning: gagal mesh part {p['name']}: {err}")

        if not sub_meshes:
            continue

        comb = sub_meshes[0]
        for sm in sub_meshes[1:]:
            comb.addMesh(sm)

        out_obj = os.path.join(out_dir, f"{key}.obj")
        comb.write(out_obj)
        print(f"  Saved: {key}.obj ({comb.CountFacets:,} facets)")

    with open(os.path.join(out_dir, "manifest.json"), "w") as handle:
        json.dump({"mode": mode_name, "layers": LAYER_LABELS, "parts": manifest_parts}, handle, indent=2)

    elapsed = time.time() - t0
    print(f"Selesai {mode_name} dalam {elapsed:.2f} detik")

def main():
    if os.path.isdir(STAGING_BASE):
        shutil.rmtree(STAGING_BASE)
    # Ekspor assembled state (explode=0.0)
    export_state("assembled", explode=0.0)
    # Ekspor exploded state (explode=0.6)
    export_state("exploded", explode=0.6)

if __name__ in ("__main__", "export_mesh_for_blender"):
    main()
