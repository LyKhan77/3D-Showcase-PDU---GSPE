#!/usr/bin/env python3
"""Compile every SCAD source and render public assemblies at three explode factors.
Uses OpenSCAD's Manifold status plus an independent binary STL edge/winding check.
Only Python standard library and the installed OpenSCAD CLI are required.
"""
from pathlib import Path
from collections import defaultdict
import concurrent.futures
import json
import struct
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCES = ROOT / "cad/apdu9953/openscad"
OUT = ROOT / "temp/apdu9953_validation"

def check_stl(path):
    data = path.read_bytes()
    count = struct.unpack_from("<I", data, 80)[0]
    assert len(data) == 84 + 50 * count, "Invalid binary STL length"
    edges = defaultdict(lambda: [0, 0])
    degenerate = 0
    volume6 = 0.0
    for i in range(count):
        values = struct.unpack_from("<12fH", data, 84 + 50*i)
        a, b, c = values[3:6], values[6:9], values[9:12]
        if len({a,b,c}) < 3:
            degenerate += 1
        for v, w in ((a,b),(b,c),(c,a)):
            key = (v,w) if v < w else (w,v)
            edges[key][0] += 1
            edges[key][1] += 1 if v < w else -1
        volume6 += a[0]*(b[1]*c[2]-b[2]*c[1]) + a[1]*(b[2]*c[0]-b[0]*c[2]) + a[2]*(b[0]*c[1]-b[1]*c[0])
    bad = sum(n != 2 for n, winding in edges.values())
    winding = sum(w != 0 for n, w in edges.values())
    return {"triangles": count, "nonmanifold_edges": bad, "inconsistent_edges": winding,
            "degenerate_triangles": degenerate, "positive_volume": volume6 > 0,
            "watertight": bad == 0 and winding == 0 and degenerate == 0}

def run_job(item):
    path, factor, extension, settings = item
    key = path.stem + "_" + str(factor).replace(".", "p") + "_" + extension
    if settings:
        key += "_" + (settings.get("VIEW_STAGE") or "only_" + next(k for k,v in settings.items() if v))
    output = OUT / (key + "." + extension)
    cmd = ["openscad", "--backend=Manifold", "--hardwarnings", "-D", "EXPLODE_FACTOR="+str(factor)]
    for name, value in settings.items():
        cmd += ["-D", name + "=" + json.dumps(value)]
    if extension == "stl":
        cmd += ["--export-format", "binstl"]
    cmd += ["-o", str(output), str(path)]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log = result.stdout + result.stderr
    (OUT / (key + ".log")).write_text(log)
    row = {"source": str(path.relative_to(ROOT)), "factor": factor, "format": extension,
           "settings": settings,
           "returncode": result.returncode, "warnings": "WARNING:" in log or "ERROR:" in log}
    if extension == "stl" and result.returncode == 0:
        row["kernel_no_error"] = "Status:     NoError" in log
        row["mesh"] = check_stl(output)
    row["pass"] = (result.returncode == 0 and not row["warnings"] and
                   (extension != "stl" or row.get("kernel_no_error", False) and row["mesh"]["watertight"] and row["mesh"]["positive_volume"]))
    print(key, "PASS" if row["pass"] else "FAIL", row.get("mesh", ""), flush=True)
    return row

if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    sources = sorted(SOURCES.rglob("*.scad"))
    selected = sys.argv[1:]
    if selected:
        sources = [p for p in sources if p.stem in selected]
    jobs = [(p, e, "csg", {}) for p in sources for e in (0, 0.6, 1)]
    jobs += [(p, e, "stl", {}) for p in sources if p.name not in ("detail_common.scad", "preview_refinement.scad") for e in (0, 0.6, 1)]
    assembly = SOURCES / "pdu_apdu9953_assembly.scad"
    if assembly in sources:
        stages = ["HOUSING", "MOUNTING", "POWER", "INTERNALS", "CONTROLS", "COMPLETE", "EXPLODED"]
        for index, name in enumerate(stages, 1):
            jobs += [(assembly, 0, ext, {"VIEW_STAGE": f"STAGE{index}_{name}"}) for ext in ("csg", "stl")]
        flags = ["SHOW_HOUSING", "SHOW_MOUNTING", "SHOW_POWER_ENTRY", "SHOW_FASCIA_EXTERNAL", "SHOW_INTERNALS"]
        for flag in flags:
            settings = {key: key == flag for key in flags}
            jobs += [(assembly, 0.6, ext, settings) for ext in ("csg", "stl")]
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        rows = list(pool.map(run_job, jobs))
    report = {"checks": len(rows), "passed": sum(r["pass"] for r in rows), "results": rows}
    (OUT / "validation_report.json").write_text(json.dumps(report, indent=2))
    print("TOTAL", report["passed"], "/", report["checks"], flush=True)
    # Mechanical mounting audit (alignment, collision probes, visibility, explode).
    audit = subprocess.run([sys.executable, str(ROOT / "cad/apdu9953/audit_mounting.py")],
                           capture_output=True, text=True)
    print(audit.stdout, flush=True)
    if audit.returncode != 0:
        print(audit.stderr, flush=True)
        sys.exit(1)
    sys.exit(0 if all(r["pass"] for r in rows) else 1)
