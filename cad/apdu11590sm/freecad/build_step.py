# =====================================================================
# build_step.py — CLI runner mandiri (headless via /opt/homebrew/bin/freecadcmd)
#   /opt/homebrew/bin/freecadcmd cad/freecad/build_step.py
# Menjalankan rakitan PDU GSPE APDU11590SM, menyimpan dokumen native
# .FCStd dan mengekspor master STEP AP214 dengan warna komponen
# (injeks STYLED_ITEM — karena console mode FreeCAD tidak menyediakan
# ViewObject, warna ditempelkan sebagai entitas AP214 pasca-ekspor).
# =====================================================================
import os
import re
import sys
import time
import traceback

CAD_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(os.path.dirname(CAD_DIR))
sys.path.insert(0, CAD_DIR)

STEP_PATH = os.path.join(ROOT_DIR, "exports", "step", "gspe_pdu_apdu11590sm.step")
FCSTD_PATH = os.path.join(ROOT_DIR, "exports", "step", "gspe_pdu_apdu11590sm.FCStd")
LOG_PATH = os.path.join(ROOT_DIR, "temp", "freecad_build_log.txt")

_log_lines = []


def log(msg):
    line = "[%7.2fs] %s" % (time.time() - _t0, msg)
    print(line)
    _log_lines.append(line)


_t0 = time.time()


# ---------------------------------------------------------------------
# Injeksi warna AP214 (STYLED_ITEM) ke STEP hasil ekspor
# ---------------------------------------------------------------------
def _refs(args):
    return [int(x) for x in re.findall(r"#(\d+)", args)]


def _faces_for_product(ents, pid):
    """Ikuti rantai PRODUCT -> ... -> CLOSED_SHELL -> ADVANCED_FACE."""
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
            faces += [f for f in _refs(a)
                      if ents.get(f, ("", ""))[0] == "ADVANCED_FACE"]
        elif t == "MANIFOLD_SOLID_BREP":
            for s in _refs(a):
                if ents.get(s, ("", ""))[0] == "CLOSED_SHELL":
                    faces += [f for f in _refs(ents[s][1])
                              if ents.get(f, ("", ""))[0] == "ADVANCED_FACE"]
    return faces


def inject_step_colors(step_path, label_colors):
    """Tambahkan entitas STYLED_ITEM/COLOUR_RGB per komponen berwarna."""
    with open(step_path) as f:
        txt = f.read()
    ents = {}
    # OCC membungkus entitas >80 kolom ke multi-baris — parse non-greedy
    # lintas baris (re.S); ';' hanya muncul di akhir entitas.
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
            new_lines.append("#%d = COLOUR_RGB('',%.3f,%.3f,%.3f);"
                             % (cid, col[0], col[1], col[2]))
            fid = nid()
            new_lines.append("#%d = FILL_AREA_STYLE_COLOUR('',#%d);" % (fid, cid))
            sfid = nid()
            new_lines.append("#%d = SURFACE_FILL_AREA_STYLE('',(#%d));" % (sfid, fid))
            ssid = nid()
            new_lines.append("#%d = SURFACE_SIDE_STYLE('',(#%d));" % (ssid, sfid))
            suid = nid()
            new_lines.append("#%d = SURFACE_STYLE_USAGE(.BOTH.,#%d);" % (suid, ssid))
            psa = nid()
            new_lines.append("#%d = PRESENTATION_STYLE_ASSIGNMENT((#%d));"
                             % (psa, suid))
            psa_by_color[col] = psa
        psa = psa_by_color[col]
        for pid in pids:
            for face in _faces_for_product(ents, pid):
                si = nid()
                new_lines.append("#%d = STYLED_ITEM('',(#%d),#%d);"
                                 % (si, psa, face))
                styled += 1

    if not new_lines:
        raise RuntimeError("Injeksi warna gagal: tidak ada entitas dibuat")

    insert_at = txt.rfind("ENDSEC;")
    txt = txt[:insert_at] + "\n".join(new_lines) + "\n" + txt[insert_at:]
    with open(step_path, "w") as f:
        f.write(txt)
    return matched, missing, styled


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
def main():
    import FreeCAD as App
    import Import

    os.makedirs(os.path.dirname(STEP_PATH), exist_ok=True)
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

    log("=== BUILD STEP GSPE PDU APDU11590SM (FreeCAD %s) ==="
        % ".".join(App.Version()[:3]))
    log("Working dir: %s" % ROOT_DIR)

    from pdu_assembly import build_assembly
    doc, parts = build_assembly()
    log("Rakitan: %d part solid terdaftar" % len(parts))

    # Validasi solid
    bad = 0
    for part in parts:
        sh = part["shape"]
        if sh.isNull() or not sh.isValid():
            log("  !! INVALID: %s" % part["name"])
            bad += 1
    if bad:
        raise RuntimeError("%d part tidak valid" % bad)
    log("Validasi solid: %d/%d valid (manifold, non-null)" % (len(parts) - bad, len(parts)))

    label_colors = {p["name"]: p["color"] for p in parts}

    # Simpan dokumen native
    doc.saveAs(FCSTD_PATH)
    log("FCStd tersimpan: %s (%d bytes)" % (FCSTD_PATH, os.path.getsize(FCSTD_PATH)))

    # Ekspor STEP AP214
    feats = [o for o in doc.Objects if o.TypeId == "Part::Feature"]
    Import.export(feats, STEP_PATH)
    step_bytes = os.path.getsize(STEP_PATH)
    log("STEP (geometry) terekspor: %s (%d bytes)" % (STEP_PATH, step_bytes))

    # Injeksi warna AP214
    matched, missing, styled = inject_step_colors(STEP_PATH, label_colors)
    log("Injeksi warna AP214: %d produk terpetakan, %d STYLED_ITEM, "
        "%d unique colour" % (matched, styled, len(set(label_colors.values()))))
    if missing:
        log("  !! produk tak terpetakan: %s" % ", ".join(missing[:10]))

    final_bytes = os.path.getsize(STEP_PATH)
    log("STEP final: %d bytes" % final_bytes)

    # Ringkasan volume per subsistem
    from collections import defaultdict
    vol = defaultdict(float)
    cnt = defaultdict(int)
    for p in parts:
        vol[p["group"]] += p["shape"].Volume
        cnt[p["group"]] += 1
    for g, _ in [s for s in
                 (("GRP_CHASSIS", 0), ("GRP_SOCKET_BANKS", 0),
                  ("GRP_NMC_CONTROLLER", 0), ("GRP_WHIP_CORD", 0),
                  ("GRP_MOUNTING_PEGS", 0))]:
        log("  %-22s %4d part  volume %12.0f mm^3"
            % (g, cnt[g], vol[g]))
    total_vol = sum(vol.values())
    log("Volume total: %.0f mm^3" % total_vol)

    log("=== BUILD SUKSES ===")

    with open(LOG_PATH, "w") as f:
        f.write("\n".join(_log_lines) + "\n")
    return 0


# freecadcmd mengeksekusi script sebagai modul ( __name__ == nama file ),
# bukan "__main__" — panggil main() tanpa guard.
try:
    sys.exit(main())
except SystemExit:
    raise
except Exception:
    log("=== BUILD GAGAL ===")
    log(traceback.format_exc())
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    with open(LOG_PATH, "w") as f:
        f.write("\n".join(_log_lines) + "\n")
    sys.exit(1)
