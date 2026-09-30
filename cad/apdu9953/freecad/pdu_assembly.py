# =====================================================================
# pdu_assembly.py — Master Assembly FreeCAD B-Rep GSPE APDU9953
# 1:1 SOLID CAD MODEL REPLIKASI DETAIL PENUH OPENSCAD
# NetShelter 9000 Switched Rack PDU (24 Outlets: 21x C13/C15 + 3x C19/C21)
# 230V 32A 1-Phase, 2x 20A Hydraulic-Magnetic Breakers, NMC3 Controller,
# IEC 60309 32A 2P+E Blue Plug, Rear Toolless Mounting Dual-Pads (1680 mm).
# =====================================================================
import os
import sys

CAD_DIR = os.path.dirname(os.path.abspath(__file__))
if CAD_DIR not in sys.path:
    sys.path.insert(0, CAD_DIR)

import FreeCAD as App
import Part

from modules._common import (
    LAYOUT_H, LAYOUT_BANK_Z, LAYOUT_BRK_Z, LAYOUT_NMC_Z,
    LAYOUT_FRONT_Y, LAYOUT_REAR_Y
)
from modules.sub_chassis import build_chassis
from modules.sub_mounting_pegs import build_mounting_pegs
from modules.sub_top_whip_cord import build_top_whip_cord
from modules.sub_breaker_box import build_breaker_box
from modules.sub_socket_bank import build_socket_bank
from modules.sub_nmc3_controller import build_nmc3_controller
from presentation import classify

PDU_H   = LAYOUT_H
FRONT_Y = LAYOUT_FRONT_Y
REAR_Y  = LAYOUT_REAR_Y

BANK1_Z = LAYOUT_BANK_Z[0]
BANK2_Z = LAYOUT_BANK_Z[1]
BANK3_Z = LAYOUT_BANK_Z[2]
BRK1_Z  = LAYOUT_BRK_Z[0]
BRK2_Z  = LAYOUT_BRK_Z[1]
NMC_Z   = LAYOUT_NMC_Z

DOC_NAME = "GSPE_PDU_APDU9953"

def _tag(parts, start, group):
    for p in parts[start:]:
        p["group"] = group
        p.update(classify(p))

SUBSYSTEMS = (
    ("GRP_HOUSING", "Housing & Chassis Extrusion"),
    ("GRP_MOUNTING", "Rear Dual-Pad Toolless Mounting"),
    ("GRP_POWER_ENTRY", "Power Whip & IEC 60309 Plug"),
    ("GRP_BREAKERS", "Hydraulic-Magnetic Circuit Breakers"),
    ("GRP_SOCKET_BANKS", "Modular 24-Outlet Switched Banks"),
    ("GRP_NMC3_CONTROLLER", "NMC3 Network Management Controller"),
)

def showcase_flags(stage="CUSTOM", explode=0.0):
    """Mengatur visibilitas subgrup sesuai stage showcase 1 s/d 7."""
    st = stage.upper()
    if st == "STAGE1_HOUSING":
        return dict(e=0.0, housing=True, mounting=False, power=False, internals=False, external=False, cover=False)
    elif st == "STAGE2_MOUNTING":
        return dict(e=0.0, housing=True, mounting=True, power=False, internals=False, external=False, cover=False)
    elif st == "STAGE3_POWER":
        return dict(e=0.0, housing=True, mounting=True, power=True, internals=False, external=False, cover=False)
    elif st == "STAGE4_INTERNALS":
        return dict(e=0.0, housing=True, mounting=True, power=True, internals=True, external=False, cover=False)
    elif st == "STAGE5_CONTROLS":
        return dict(e=0.0, housing=True, mounting=True, power=True, internals=True, external=True, cover=True)
    elif st == "STAGE6_COMPLETE":
        return dict(e=0.0, housing=True, mounting=True, power=True, internals=True, external=True, cover=True)
    elif st == "STAGE7_EXPLODED":
        return dict(e=0.6, housing=True, mounting=True, power=True, internals=True, external=True, cover=True)
    else: # CUSTOM
        return dict(e=explode, housing=True, mounting=True, power=True, internals=True, external=True, cover=True)

def collect_parts(doc=None, stage="CUSTOM", explode=0.0):
    """Membangun dan mengumpulkan seluruh solid B-Rep APDU9953 dengan detail 1:1."""
    cfg = showcase_flags(stage, explode)
    e = cfg["e"]
    parts = []

    # 1. Housing & Chassis (Extrusion, Caps, Fasteners, Plates)
    n0 = len(parts)
    build_chassis(parts, prefix="CHASSIS", explode=e, doc=doc,
                  show_housing=cfg["housing"], show_front_cover=cfg["cover"])
    _tag(parts, n0, "GRP_HOUSING")

    # 2. Mounting System (Dual Pads, Pegs, Ground Stud & Symbol)
    n0 = len(parts)
    build_mounting_pegs(parts, prefix="MOUNT", rear_y=REAR_Y, explode=e, doc=doc,
                        show_mounting=cfg["mounting"])
    _tag(parts, n0, "GRP_MOUNTING")

    # 3. Power Entry Whip Cord & Plug
    n0 = len(parts)
    build_top_whip_cord(parts, prefix="WHIP", cord_len=500.0, top_z=PDU_H,
                        explode=e, doc=doc,
                        show_power_entry=cfg["power"], show_whip=cfg["power"])
    _tag(parts, n0, "GRP_POWER_ENTRY")

    # 4. Circuit Breakers (Bank 1 & Bank 2)
    n0 = len(parts)
    build_breaker_box(parts, prefix="BRK1", bank_label="Bank 1", center_z=BRK1_Z,
                      front_y=FRONT_Y, explode=e, doc=doc,
                      show_housing=cfg["housing"],
                      show_fascia_external=cfg["external"],
                      show_internals=cfg["internals"],
                      show_front_cover=cfg["cover"])
    build_breaker_box(parts, prefix="BRK2", bank_label="Bank 2", center_z=BRK2_Z,
                      front_y=FRONT_Y, explode=e, doc=doc,
                      show_housing=cfg["housing"],
                      show_fascia_external=cfg["external"],
                      show_internals=cfg["internals"],
                      show_front_cover=cfg["cover"])
    _tag(parts, n0, "GRP_BREAKERS")

    # 5. Socket Banks (3 banks x 8 outlets = 24 outlets)
    n0 = len(parts)
    build_socket_bank(parts, prefix="BANK1", bank_id=1, center_z=BANK1_Z,
                      front_y=FRONT_Y, explode=e, doc=doc,
                      show_housing=cfg["housing"],
                      show_fascia_external=cfg["external"],
                      show_internals=cfg["internals"],
                      show_front_cover=cfg["cover"],
                      show_busbars=cfg["internals"])
    build_socket_bank(parts, prefix="BANK2", bank_id=2, center_z=BANK2_Z,
                      front_y=FRONT_Y, explode=e, doc=doc,
                      show_housing=cfg["housing"],
                      show_fascia_external=cfg["external"],
                      show_internals=cfg["internals"],
                      show_front_cover=cfg["cover"],
                      show_busbars=cfg["internals"])
    build_socket_bank(parts, prefix="BANK3", bank_id=3, center_z=BANK3_Z,
                      front_y=FRONT_Y, explode=e, doc=doc,
                      show_housing=cfg["housing"],
                      show_fascia_external=cfg["external"],
                      show_internals=cfg["internals"],
                      show_front_cover=cfg["cover"],
                      show_busbars=cfg["internals"])
    _tag(parts, n0, "GRP_SOCKET_BANKS")

    # 6. NMC3 Controller
    n0 = len(parts)
    build_nmc3_controller(parts, prefix="NMC3", center_z=NMC_Z,
                          front_y=FRONT_Y, explode=e, doc=doc,
                          show_fascia_external=cfg["external"],
                          show_internals=cfg["internals"])
    _tag(parts, n0, "GRP_NMC3_CONTROLLER")

    return parts

def build_document(doc_name=DOC_NAME, stage="CUSTOM", explode=0.0):
    """Membuat dokumen FreeCAD native dengan grup pohon hirarkis."""
    doc = App.newDocument(doc_name)
    App.setActiveDocument(doc.Name)

    # Inisialisasi Group Tree
    group_map = {}
    for gid, glabel in SUBSYSTEMS:
        grp = doc.addObject("App::DocumentObjectGroup", gid)
        grp.Label = glabel
        group_map[gid] = grp

    parts = collect_parts(doc=doc, stage=stage, explode=explode)

    # Tambahkan setiap part ke dokumen & grupnya
    for p in parts:
        obj = doc.addObject("Part::Feature", p["name"])
        obj.Shape = p["shape"]
        obj.Label = p["name"]

        gid = p.get("group", "GRP_HOUSING")
        if gid in group_map:
            group_map[gid].addObject(obj)

    doc.recompute()
    return doc, parts
