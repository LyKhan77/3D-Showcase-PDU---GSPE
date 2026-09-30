# =====================================================================
# sub_breaker_box.py — Plat breaker per bank (24 x 68 mm) + rocker 20A
# + sekrup + label ON/OFF & B#/fasa. Konversi dari sub_breaker_box.scad.
# Warna plat selang-seling GSPE Navy #003674 / Cream #FAFFD8.
# =====================================================================
from FreeCAD import Vector as V
import Part
from ._common import (P, validate, box, cyl, fuse_all, text3d,
                      GSPE_NAVY, GSPE_CREAM, BRK_BEZEL, ROCKER_BLACK,
                      SCREW_BLACK, TEXT_WHITE)

BRK_W = 24.0
BRK_H = 68.0
EPS = 0.05


def _breaker_screw(parts, prefix, x, y, z):
    head = cyl(4.5, 1.0, x, y, z, dirv=(0, 1, 0))
    a = box(3.0, 0.5, 0.8, x - 1.5, y - 0.5, z - 0.4)
    b = box(0.8, 0.5, 3.0, x - 0.4, y - 0.5, z - 1.5)
    s = fuse_all([head, a, b])
    validate(prefix, s)
    P(parts, prefix, s, SCREW_BLACK)


def build_breaker_plate(parts, prefix, bank_id, phase_str,
                        plate_color, text_color, offset=(0, 0, 0)):
    reg = []
    # ---- Plat dasar + cutout rocker tengah ----
    plate = box(BRK_W, 2.0, BRK_H, -BRK_W / 2, -1.0, -BRK_H / 2)
    win = box(15.0, 4.0, 32.0, -7.5, -2.0, -16.0)
    plate = plate.cut(win)
    validate(prefix + "_PLATE", plate)
    P(reg, prefix + "_PLATE", plate, plate_color)

    # ---- Sekrup Phillips atas & bawah ----
    _breaker_screw(reg, prefix + "_SCREW_TOP", 0, -1.2, BRK_H / 2 - 6.0)
    _breaker_screw(reg, prefix + "_SCREW_BOT", 0, -1.2, -BRK_H / 2 + 20.0)

    # ---- Bezel frame rocker ----
    P(reg, prefix + "_BEZEL", box(14.0, 2.0, 30.0, -7.0, -2.0, -15.0),
      BRK_BEZEL)

    # ---- Rocker 20A (miring -5 deg, sumbu X) ----
    rocker = box(11.0, 2.5, 27.0, 0, 0, 0)
    rocker.rotate(V(0, 0, 0), V(1, 0, 0), -5)
    rocker.translate(V(-5.5, -3.2, -13.5))
    validate(prefix + "_ROCKER", rocker)
    P(reg, prefix + "_ROCKER", rocker, ROCKER_BLACK)

    # ---- Teks ON 20 / OFF ----
    P(reg, prefix + "_TXT_ON",
      text3d("ON", 2.4, 0.3, 0, -3.5, 4.0), TEXT_WHITE)
    P(reg, prefix + "_TXT_20",
      text3d("20", 2.0, 0.3, 0, -3.5, 0.8), TEXT_WHITE)
    P(reg, prefix + "_TXT_OFF",
      text3d("OFF", 2.0, 0.3, 0, -3.5, -8.0), TEXT_WHITE)

    # ---- Label B# dan fasa (rotasi 90 deg) ----
    lbl_z = -BRK_H / 2 + 7.5
    P(reg, prefix + "_TXT_BID",
      text3d("B%d" % bank_id, 3.6, 0.4, 3.5, -1.5, lbl_z, rotz=90),
      text_color)
    P(reg, prefix + "_TXT_PHASE",
      text3d(phase_str, 2.6, 0.4, -3.5, -1.5, lbl_z, rotz=90),
      text_color)

    if any(offset):
        for p in reg:
            p["shape"].translate(V(*offset))
    parts.extend(reg)
    return parts
