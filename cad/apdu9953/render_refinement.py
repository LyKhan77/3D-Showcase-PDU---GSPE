#!/usr/bin/env python3
"""Render detail views and presentation stages using actual OpenSCAD geometry."""
from pathlib import Path
import argparse
import concurrent.futures
import json
import subprocess

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "cad/apdu9953/openscad/preview_refinement.scad"
ASSEMBLY = SOURCE.with_name("pdu_apdu9953_assembly.scad")
STAGES = {"stage" + str(i): "STAGE" + str(i) + "_" + name for i, name in enumerate(
    ["HOUSING", "MOUNTING", "POWER", "INTERNALS", "CONTROLS", "COMPLETE", "EXPLODED"], 1)}
JOBS = {
    "mounting": ("apdu9953_close_mounting_dualpad.png", "145,505,1834,0,27,1755", "1500,1800", 0),
    "grounding": ("apdu9953_close_grounding.png", "80,280,170,0,23,110", "1200,1500", 0),
    "stage1": ("apdu9953_stage1_housing.png", "-600,-3800,1350,0,0,914.5", "1400,2800", 0),
    "stage2": ("apdu9953_stage2_mounting.png", "650,3800,1350,0,0,914.5", "1400,2800", 0),
    "stage3": ("apdu9953_stage3_power.png", "-700,-4900,1800,0,0,1240", "1400,3000", 0),
    "stage4": ("apdu9953_stage4_internals.png", "-600,-4900,1800,0,0,1240", "1600,3200", 0),
    "stage5": ("apdu9953_stage5_controls.png", "-700,-4900,1800,0,0,1240", "1400,3000", 0),
    "stage6": ("apdu9953_stage6_complete.png", "-700,-4900,1800,0,0,1240", "1400,3000", 0),
    "stage7": ("apdu9953_stage7_exploded.png", "-2700,-4200,2040,0,50,1240", "2000,3200", 0.6),
    "ports": ("apdu9953_close_lan_revised.png", "48,-260,42,0,0,-18", "1500,1600", 0),
    "breaker": ("apdu9953_close_breaker_revised.png", "95,-230,72,0,0,0", "1200,1400", 0),
    "sockets": ("apdu9953_close_sockets_revised.png", "65,-245,63.25,0,0,20.25", "1200,1500", 0),
    "controller": ("apdu9953_close_controller_revised.png", "105,-560,145,0,0,0", "1200,2000", 0),
    "exploded": ("apdu9953_exploded_view.png", "-2700,-3900,2070,0,45,914.5", "1800,3200", 0.6),
    "sidefast": ("apdu9953_side_fasteners.png", "140,-70,150,28.5,-4,100", "1300,900", 0),
    "intmount": ("apdu9953_internal_mounting.png", "-190,150,120,5,20,0", "1100,1100", 0),
    "ctrmount": ("apdu9953_controller_mounting.png", "85,-125,155,0,20,60", "1100,1300", 0),
    "intmountexpl": ("apdu9953_internal_mounting_exploded.png", "-210,215,135,0,25,0", "1300,1300", 0.6),
}

def render(item):
    part, (filename, camera, size, factor) = item
    output = ROOT / "previews" / filename
    output.parent.mkdir(exist_ok=True, parents=True)
    cmd = ["openscad", "--hardwarnings", "--backend=Manifold", "--render",
           "--projection=o", "--colorscheme=Tomorrow", "--imgsize=" + size,
           "--camera=" + camera, "-D", 'PREVIEW_PART="' + part + '"',
           "-D", "EXPLODE_FACTOR=" + str(factor)]
    stage = STAGES.get(part, "STAGE2_MOUNTING" if part in ("mounting", "grounding") else None)
    if stage:
        cmd += ["-D", 'VIEW_STAGE="' + stage + '"']
        if part in STAGES:
            cmd += ["--viewall"]
    else:
        cmd += ["-D", "SHOW_WHIP=false"]
    cmd += ["-o", str(output), str(ASSEMBLY if stage else SOURCE)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    logs = ROOT / "temp/apdu9953_validation"
    logs.mkdir(exist_ok=True, parents=True)
    (logs / (part + ".preview.log")).write_text(result.stdout + result.stderr)
    passed = result.returncode == 0 and output.exists() and "WARNING:" not in result.stderr and "ERROR:" not in result.stderr
    print(part, "PASS" if passed else "FAIL", flush=True)
    if not passed:
        raise RuntimeError(result.stderr)
    return {"part": part, "output": str(output.relative_to(ROOT)), "view_stage": stage,
            "explode_factor": factor, "command": cmd}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("parts", nargs="*", choices=list(JOBS), default=list(JOBS))
    args = parser.parse_args()
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(render, [(p, JOBS[p]) for p in args.parts]))
    (ROOT / "temp/apdu9953_validation/render_manifest.json").write_text(json.dumps(results, indent=2))
