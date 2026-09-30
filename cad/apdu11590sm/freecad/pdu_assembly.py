# =====================================================================
# pdu_assembly.py — Script master rakitan FreeCAD PDU GSPE APDU11590SM
# Konversi B-Rep dari pdu_apdu11590sm_assembly.scad (Tahap 1 OpenSCAD).
# Koordinat global Z identik dengan OpenSCAD:
#   Bank bawah b1..b6 : Z = 450 + (b-1)*68 + 34  (484 s/d 824)
#   NMC controller    : Z = 1000, Y = FRONT_Y + 45 - 0.8
#   Bank atas  b7..b12: Z = 1250 + (b-7)*68 + 34 (1284 s/d 1624)
#   Mounting pegs     : Z = 99 & 1931, Y = REAR_Y
#   Whip cord + plug  : Z = 2030 ke atas
# =====================================================================
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import FreeCAD as App

from modules.sub_chassis import build_chassis
from modules.sub_socket_bank import build_socket_bank
from modules.sub_nmc_controller import build_nmc_controller
from modules.sub_top_whip_cord import build_whip_cord
from modules.sub_mounting_pegs import build_mounting_pegs

PDU_H = 2030.0
PDU_W = 85.0
PDU_D = 85.0
FRONT_Y = -PDU_D / 2          # -42.5 mm
REAR_Y = PDU_D / 2            # +42.5 mm

LOWER_Z_START = 450.0
UPPER_Z_START = 1250.0
BANK_PITCH = 68.0

DOC_NAME = "GSPE_PDU_APDU11590SM"

# Sub-sistem untuk grup dokumen & log
SUBSYSTEMS = (
    ("GRP_CHASSIS", "CHASSIS"),
    ("GRP_SOCKET_BANKS", "BANK"),
    ("GRP_NMC_CONTROLLER", "NMC"),
    ("GRP_WHIP_CORD", "WHIP"),
    ("GRP_MOUNTING_PEGS", "PEG"),
)


def collect_parts():
    """Bangun seluruh geometri; kembalikan daftar part lokal (belum offset bank)."""
    parts = []
    n = len(parts)
    build_chassis(parts)
    for p in parts[n:]:
        p["group"] = "GRP_CHASSIS"

    # 12 bank soket (bawah 1-6, atas 7-12)
    for b in range(1, 13):
        z_start = LOWER_Z_START if b <= 6 else UPPER_Z_START
        z = z_start + ((b - 1) if b <= 6 else (b - 7)) * BANK_PITCH + BANK_PITCH / 2
        n = len(parts)
        build_socket_bank(parts, "B%02d" % b, b)
        for p in parts[n:]:
            p["shape"].translate(App.Vector(0, FRONT_Y, z))
            p["group"] = "GRP_SOCKET_BANKS"

    # NMC3 controller cassette
    n = len(parts)
    build_nmc_controller(parts, "NMC")
    for p in parts[n:]:
        p["shape"].translate(App.Vector(0, FRONT_Y + 45.0 - 0.8, 1000.0))
        p["group"] = "GRP_NMC_CONTROLLER"

    # Whip cord + plug IEC 60309
    n = len(parts)
    build_whip_cord(parts, "WHIP", offset=(0, 0, PDU_H))
    for p in parts[n:]:
        p["group"] = "GRP_WHIP_CORD"

    # Toolless mounting pegs belakang
    n = len(parts)
    build_mounting_pegs(parts, "PEG", rear_y=REAR_Y)
    for p in parts[n:]:
        p["group"] = "GRP_MOUNTING_PEGS"

    return parts


def build_document(parts):
    """Buat dokumen FreeCAD berisi Part::Feature per part + grup."""
    doc = App.newDocument(DOC_NAME)
    App.setActiveDocument(doc.Name)

    groups = {}
    for gname, _prefix in SUBSYSTEMS:
        g = doc.addObject("App::DocumentObjectGroup", gname)
        g.Label = gname
        groups[gname] = g

    seen = set()
    for i, part in enumerate(parts):
        name = part["name"]
        if name in seen:
            raise RuntimeError("Duplikat nama part: %s" % name)
        seen.add(name)
        feat = doc.addObject("Part::Feature", name)
        feat.Label = name
        feat.Shape = part["shape"]
        groups[part["group"]].addObject(feat)

    doc.recompute()
    return doc


def build_assembly():
    parts = collect_parts()
    doc = build_document(parts)
    return doc, parts


if __name__ == "__main__":
    doc, parts = build_assembly()
    print("Assembly OK: %d parts" % len(parts))
