# =====================================================================
# build_step.py — Headless CLI Runner FreeCAD untuk GSPE APDU9953
# Menjalankan assembly B-Rep solid, menyimpan dokumen native .FCStd,
# dan mengekspor master STEP AP214 lengkap dengan injeksi warna
# (STYLED_ITEM / COLOUR_RGB) untuk kompatibilitas CAD & Blender.
# =====================================================================
import os
import re
import sys
import time
import traceback

CAD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(CAD_DIR)))
if CAD_DIR not in sys.path:
    sys.path.insert(0, CAD_DIR)

STEP_PATH = os.path.join(ROOT_DIR, "exports", "apdu9953", "step", "gspe_pdu_apdu9953.step")
FCSTD_PATH = os.path.join(ROOT_DIR, "exports", "apdu9953", "step", "gspe_pdu_apdu9953.FCStd")
LOG_PATH = os.path.join(ROOT_DIR, "temp", "apdu9953_freecad_build_log.txt")

_t0 = time.time()
_log_lines = []

def log(msg):
    line = "[%7.2fs] %s" % (time.time() - _t0, msg)
    print(line)
    _log_lines.append(line)

def _refs(args):
    return [int(x) for x in re.findall(r"#(\d+)", args)]

def _faces_for_product(ents, pid):
    """Mengikuti rantai PRODUCT -> ... -> CLOSED_SHELL -> ADVANCED_FACE."""
    pdf = next((i for i, (t, a) in ents.items()
                if t == "PRODUCT_DEFINITION_FORMATION" and pid in _refs(a)), None)
    if pdf is None:
        return []
    pd = next((i for i, (t, a) in ents.items()
               if t == "PRODUCT_DEFINITION" and pdf in _refs(a)), None)
    if pd is None:
        return []
    pds = next((i for i, (t, a) in ents.items()
                if t == "PRODUCT_DEFINITION_SHAPE" and pd in _refs(a)), None)
    if pds is None:
        return []
    sdr = next((i for i, (t, a) in ents.items()
                if t == "SHAPE_DEFINITION_REPRESENTATION" and pds in _refs(a)), None)
    if sdr is None:
        return []
    rep = next((r for r in _refs(ents[sdr][1])
                if ents.get(r, ("", ""))[0] == "ADVANCED_BREP_SHAPE_REPRESENTATION"), None)
    if rep is None:
        return []
    faces = []
    for r in _refs(ents[rep][1]):
        t, a = ents.get(r, ("", ""))
        if t == "CLOSED_SHELL":
            faces += [f for f in _refs(a) if ents.get(f, ("", ""))[0] == "ADVANCED_FACE"]
        elif t == "MANIFOLD_SOLID_BREP":
            for s in _refs(a):
                if ents.get(s, ("", ""))[0] == "CLOSED_SHELL":
                    faces += [f for f in _refs(ents[s][1]) if ents.get(f, ("", ""))[0] == "ADVANCED_FACE"]
    return faces

def inject_step_colors(step_path, label_colors):
    """Tambahkan entitas STYLED_ITEM/COLOUR_RGB per komponen berwarna."""
    with open(step_path) as f:
        txt = f.read()
    ents = {}
    for m in re.finditer(r"^#(\d+) = ([A-Z_0-9]+)\((.*?)\);\s*$", txt, re.M | re.S):
        ents[int(m.group(1))] = (m.group(2), m.group(3))
    products = {i: re.match(r"'([^']*)'", a).group(1)
                for i, (t, a) in ents.items() if t == "PRODUCT"}

    next_id = max(ents) + 1
    new_lines = []
    psa_by_color = {}
    styled = 0
    missing = []
    matched = 0

    def nid():
        nonlocal next_id
        v = next_id
        next_id += 1
        return v

    for label, col in label_colors.items():
        pids = [i for i, n in products.items() if n == label]
        if not pids:
            missing.append(label)
            continue
        matched += 1
        col = tuple(round(c, 3) for c in col)
        if col not in psa_by_color:
            cid = nid()
            new_lines.append("#%d = COLOUR_RGB('',%.3f,%.3f,%.3f);" % (cid, col[0], col[1], col[2]))
            fid = nid()
            new_lines.append("#%d = FILL_AREA_STYLE_COLOUR('',#%d);" % (fid, cid))
            sfid = nid()
            new_lines.append("#%d = SURFACE_FILL_AREA_STYLE('',(#%d));" % (sfid, fid))
            ssid = nid()
            new_lines.append("#%d = SURFACE_SIDE_STYLE('',(#%d));" % (ssid, sfid))
            suid = nid()
            new_lines.append("#%d = SURFACE_STYLE_USAGE(.BOTH.,#%d);" % (suid, ssid))
            psa = nid()
            new_lines.append("#%d = PRESENTATION_STYLE_ASSIGNMENT((#%d));" % (psa, suid))
            psa_by_color[col] = psa
        psa = psa_by_color[col]
        for pid in pids:
            for face in _faces_for_product(ents, pid):
                si = nid()
                new_lines.append("#%d = STYLED_ITEM('',(#%d),#%d);" % (si, psa, face))
                styled += 1

    if not new_lines:
        log("Peringatan: tidak ada entitas warna baru yang dibuat")
        return matched, missing, styled

    insert_at = txt.rfind("ENDSEC;")
    txt = txt[:insert_at] + "\n".join(new_lines) + "\n" + txt[insert_at:]
    with open(step_path, "w") as f:
        f.write(txt)
    return matched, missing, styled

def main():
    import FreeCAD as App
    import Import

    os.makedirs(os.path.dirname(STEP_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    log("=== BUILD STEP GSPE PDU APDU9953 (FreeCAD %s) ===" % ".".join(App.Version()[:3]))
    log("Working dir: %s" % ROOT_DIR)

    from pdu_assembly import build_document
    doc, parts = build_document()
    log("Dokumen FreeCAD '%s' berhasil dibangun dengan %d komponen" % (doc.Name, len(parts)))

    # Simpan .FCStd
    doc.saveAs(FCSTD_PATH)
    log("Dokumen native tersimpan: %s (%.1f KB)" % (FCSTD_PATH, os.path.getsize(FCSTD_PATH) / 1024))

    # Ekspor master STEP
    objs = [doc.getObject(p["name"]) for p in parts if doc.getObject(p["name"]) is not None]
    Import.export(objs, STEP_PATH)
    log("STEP awal diekspor: %s (%.1f KB)" % (STEP_PATH, os.path.getsize(STEP_PATH) / 1024))

    # Injeksi warna AP214
    label_colors = {p["name"]: p["color"] for p in parts}
    matched, missing, styled = inject_step_colors(STEP_PATH, label_colors)
    log("Injeksi warna AP214: %d part matched, %d missing, %d face styled" % (matched, len(missing), styled))
    log("Master STEP final: %s (%.1f KB)" % (STEP_PATH, os.path.getsize(STEP_PATH) / 1024))

    with open(LOG_PATH, "w") as f:
        f.write("\n".join(_log_lines) + "\n")
    log("Log build tersimpan: %s" % LOG_PATH)
    print("BUILD STEP COMPLETE SUCCESS")

if __name__ in ("__main__", "build_step"):
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        sys.exit(1)
