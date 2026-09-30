# =====================================================================
# sub_mounting_pegs.py — 2x toolless mushroom mounting button di muka
# belakang chassis (Y=+42.5), pitch vertikal 1832 mm (Z=99 & Z=1931).
# Konversi dari sub_mounting_pegs.scad.
# =====================================================================
from FreeCAD import Vector as V
from ._common import P, validate, cyl, cone, PEG_ZINC

PEG_SPACING = 1832.0
PEG_HEAD_DIA = 12.0
PEG_HEAD_T = 3.0
PEG_NECK_DIA = 6.0
PEG_NECK_H = 5.0
PEG_BASE_DIA = 10.0
PEG_BASE_T = 2.0

# Z global kedua peg (Tahap 1): tengah PDU 1015 +/- 916
PEG_Z1 = 99.0
PEG_Z2 = 1931.0


def build_mounting_pegs(parts, prefix="PEG", rear_y=42.5):
    for i, z in enumerate((PEG_Z1, PEG_Z2), start=1):
        p = "%s%d_" % (prefix, i)
        base = cyl(PEG_BASE_DIA, PEG_BASE_T, 0, rear_y, z, dirv=(0, 1, 0))
        neck = cyl(PEG_NECK_DIA, PEG_NECK_H, 0, rear_y + PEG_BASE_T, z,
                   dirv=(0, 1, 0))
        head = cyl(PEG_HEAD_DIA, PEG_HEAD_T - 1.2, 0,
                   rear_y + PEG_BASE_T + PEG_NECK_H, z, dirv=(0, 1, 0))
        cham = cone(PEG_HEAD_DIA, PEG_HEAD_DIA - 3, 1.2, 0, 0, 0)
        cham.rotate(V(0, 0, 0), V(1, 0, 0), -90)
        cham.translate(V(0, rear_y + PEG_BASE_T + PEG_NECK_H + PEG_HEAD_T - 1.2, z))
        peg = base.fuse(neck).fuse(head).fuse(cham)
        validate(p + "BUTTON", peg)
        P(parts, p + "BUTTON", peg, PEG_ZINC)
    return parts
